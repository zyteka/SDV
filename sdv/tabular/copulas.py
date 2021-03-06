"""Wrappers around copulas models."""

import logging

import copulas
import copulas.multivariate
import copulas.univariate
import numpy as np
import pandas as pd

from sdv.metadata import Table
from sdv.tabular.base import BaseTabularModel
from sdv.tabular.utils import (
    check_matrix_symmetric_positive_definite, flatten_dict, make_positive_definite, square_matrix,
    unflatten_dict)

LOGGER = logging.getLogger(__name__)


class GaussianCopula(BaseTabularModel):
    """Model wrapping ``copulas.multivariate.GaussianMultivariate`` copula.

    Args:
        field_names (list[str]):
            List of names of the fields that need to be modeled
            and included in the generated output data. Any additional
            fields found in the data will be ignored and will not be
            included in the generated output.
            If ``None``, all the fields found in the data are used.
        field_types (dict[str, dict]):
            Dictinary specifying the data types and subtypes
            of the fields that will be modeled. Field types and subtypes
            combinations must be compatible with the SDV Metadata Schema.
        field_transformers (dict[str, str]):
            Dictinary specifying which transformers to use for each field.
            Available transformers are:

                * ``integer``: Uses a ``NumericalTransformer`` of dtype ``int``.
                * ``float``: Uses a ``NumericalTransformer`` of dtype ``float``.
                * ``categorical``: Uses a ``CategoricalTransformer`` without gaussian noise.
                * ``categorical_fuzzy``: Uses a ``CategoricalTransformer`` adding gaussian noise.
                * ``one_hot_encoding``: Uses a ``OneHotEncodingTransformer``.
                * ``label_encoding``: Uses a ``LabelEncodingTransformer``.
                * ``boolean``: Uses a ``BooleanTransformer``.
                * ``datetime``: Uses a ``DatetimeTransformer``.

        anonymize_fields (dict[str, str]):
            Dict specifying which fields to anonymize and what faker
            category they belong to.
        primary_key (str):
            Name of the field which is the primary key of the table.
        constraints (list[Constraint, dict]):
            List of Constraint objects or dicts.
        table_metadata (dict or metadata.Table):
            Table metadata instance or dict representation.
            If given alongside any other metadata-related arguments, an
            exception will be raised.
            If not given at all, it will be built using the other
            arguments or learned from the data.
        distribution (copulas.univariate.Univariate or str):
            Copulas univariate distribution to use. To choose from:

                * ``univariate``: Let ``copulas`` select the optimal univariate distribution.
                  This may result in non-parametric models being used.
                * ``parametric``: Let ``copulas`` select the optimal univariate distribution,
                  but restrict the selection to parametric distributions only.
                * ``bounded``: Let ``copulas`` select the optimal univariate distribution,
                  but restrict the selection to bounded distributions only.
                  This may result in non-parametric models being used.
                * ``semi_bounded``: Let ``copulas`` select the optimal univariate distribution,
                  but restrict the selection to semi-bounded distributions only.
                  This may result in non-parametric models being used.
                * ``parametric_bounded``: Let ``copulas`` select the optimal univariate
                  distribution, but restrict the selection to parametric and bounded distributions
                  only.
                * ``parametric_semi_bounded``: Let ``copulas`` select the optimal univariate
                  distribution, but restrict the selection to parametric and semi-bounded
                  distributions only.
                * ``gaussian``: Use a Gaussian distribution.
                * ``gamma``: Use a Gamma distribution.
                * ``beta``: Use a Beta distribution.
                * ``student_t``: Use a Student T distribution.
                * ``gussian_kde``: Use a GaussianKDE distribution. This model is non-parametric,
                  so using this will make ``get_parameters`` unusable.
                * ``truncated_gaussian``: Use a Truncated Gaussian distribution.

        default_distribution (copulas.univariate.Univariate or str):
            Copulas univariate distribution to use by default. To choose from the list
            of possible ``distribution`` values. Defaults to ``parametric``.

        categorical_transformer (str):
            Type of transformer to use for the categorical variables, to choose
            from:

                * ``one_hot_encoding``: Apply a OneHotEncodingTransformer to the
                  categorical column, which replaces the  column with one boolean
                  column for each possible category, indicating whether each row
                  had that value or not.
                * ``label_encoding``: Apply a LabelEncodingTransformer, which
                  replaces the value of each category with an integer value that
                  acts as its *label*.
                * ``categorical``: Apply CategoricalTransformer, which replaces
                  each categorical value with a float number in the `[0, 1]` range
                  which is inversely proportional to the frequency of that category.
                * ``categorical_fuzzy``: Apply a CategoricalTransformer with the
                  ``fuzzy`` argument set to ``True``, which makes it add gaussian
                  noise around each value.
    """

    _distribution = None
    _categorical_transformer = None
    _model = None

    _DISTRIBUTIONS = {
        'univariate': copulas.univariate.Univariate,
        'parametric': copulas.univariate.Univariate(
            parametric=copulas.univariate.ParametricType.PARAMETRIC),
        'bounded': copulas.univariate.Univariate(
            bounded=copulas.univariate.BoundedType.BOUNDED),
        'semi_bounded': copulas.univariate.Univariate(
            bounded=copulas.univariate.BoundedType.SEMI_BOUNDED),
        'parametric_bounded': copulas.univariate.Univariate(
            parametric=copulas.univariate.ParametricType.PARAMETRIC,
            bounded=copulas.univariate.BoundedType.BOUNDED,
        ),
        'parametric_semi_bounded': copulas.univariate.Univariate(
            parametric=copulas.univariate.ParametricType.PARAMETRIC,
            bounded=copulas.univariate.BoundedType.SEMI_BOUNDED,
        ),
        'gaussian': copulas.univariate.GaussianUnivariate,
        'gamma': copulas.univariate.GammaUnivariate,
        'beta': copulas.univariate.BetaUnivariate,
        'student_t': copulas.univariate.StudentTUnivariate,
        'gaussian_kde': copulas.univariate.GaussianKDE,
        'truncated_gaussian': copulas.univariate.TruncatedGaussian,
    }

    _HYPERPARAMETERS = {
        'distribution': {
            'type': 'str or copulas.univariate.Univariate',
            'default': 'Univariate',
            'description': 'Univariate distribution to use to model each column',
            'choices': [
                'Univariate',
                'Gaussian',
                'Gamma',
                'Beta',
                'StudentT',
                'GaussianKDE',
                'TruncatedGaussian',
            ]
        },
        'categorical_transformer': {
            'type': 'str',
            'default': 'one_hot_encoding',
            'description': 'Type of transformer to use for the categorical variables',
            'choices': [
                'categorical',
                'categorical_fuzzy',
                'one_hot_encoding',
                'label_encoding'
            ]
        }
    }
    _DEFAULT_TRANSFORMER = 'one_hot_encoding'

    def _get_distribution(self, table_data):
        default = self._DISTRIBUTIONS.get(self._default_distribution, self._default_distribution)
        if self._distribution is None:
            return {
                name: default
                for name in table_data.columns
            }

        if not isinstance(self._distribution, dict):
            distribution = self._DISTRIBUTIONS.get(self._distribution, self._distribution)
            return {
                name: distribution
                for name in table_data.columns
            }

        distributions = {}
        for column in table_data.columns:
            distribution = self._distribution.get(column)
            if not distribution:
                distribution = default
            else:
                distribution = self._DISTRIBUTIONS.get(distribution, distribution)

            distributions[column] = distribution

        return distributions

    def __init__(self, field_names=None, field_types=None, field_transformers=None,
                 anonymize_fields=None, primary_key=None, constraints=None, table_metadata=None,
                 distribution=None, default_distribution=None, categorical_transformer=None):

        if isinstance(table_metadata, dict):
            table_metadata = Table.from_dict(table_metadata)

        if table_metadata:
            model_kwargs = table_metadata.get_model_kwargs(self.__class__.__name__)
            if model_kwargs:
                if distribution is None:
                    distribution = model_kwargs['distribution']

                if categorical_transformer is None:
                    categorical_transformer = model_kwargs['categorical_transformer']

        self._distribution = distribution
        self._default_distribution = default_distribution or 'parametric'

        categorical_transformer = categorical_transformer or self._DEFAULT_TRANSFORMER
        self._categorical_transformer = categorical_transformer
        self._DTYPE_TRANSFORMERS = {'O': categorical_transformer}

        super().__init__(
            field_names=field_names,
            primary_key=primary_key,
            field_types=field_types,
            anonymize_fields=anonymize_fields,
            constraints=constraints,
            table_metadata=table_metadata
        )

    def get_distributions(self):
        """Get the arguments needed to reproduce this model.

        Additional arguments include:
            - Distribution found for each column
            - categorical_transformer

        Returns:
            dict:
                Dictionary containing the categorical transformer used
                and the distributions used or detected for each column.
        """
        parameters = self._model.to_dict()
        univariates = parameters['univariates']
        columns = parameters['columns']

        distributions = {}
        for column, univariate in zip(columns, univariates):
            distributions[column] = univariate['type']

        return distributions

    def _update_metadata(self):
        """Add arguments needed to reproduce this model to the Metadata.

        Additional arguments include:
            - Distribution found for each column
            - categorical_transformer
        """
        class_name = self.__class__.__name__
        model_kwargs = self._metadata.get_model_kwargs(class_name)
        if not model_kwargs:
            distributions = self.get_distributions()
            self._metadata.set_model_kwargs(class_name, {
                'distribution': distributions,
                'categorical_transformer': self._categorical_transformer,
            })

    def _fit(self, table_data):
        """Fit the model to the table.

        Args:
            table_data (pandas.DataFrame):
                Data to be fitted.
        """
        self._distribution = self._get_distribution(table_data)
        self._model = copulas.multivariate.GaussianMultivariate(distribution=self._distribution)

        LOGGER.debug('Fitting %s to table %s; shape: %s', self._model.__class__.__name__,
                     self._metadata.name, table_data.shape)
        self._model.fit(table_data)
        self._update_metadata()

    def _sample(self, num_rows):
        """Sample the indicated number of rows from the model.

        Args:
            num_rows (int):
                Amount of rows to sample.

        Returns:
            pandas.DataFrame:
                Sampled data.
        """
        return self._model.sample(num_rows)

    def _get_likelihood(self, table_data):
        """Get the likelihood of each row belonging to this table."""
        return self._model.probability_density(table_data)

    def get_parameters(self):
        """Get copula model parameters.

        Compute model ``covariance`` and ``distribution.std``
        before it returns the flatten dict.

        Returns:
            dict:
                Copula parameters.

        Raises:
            NonParametricError:
                If a non-parametric distribution has been used.
        """
        params = self._model.to_dict()

        covariance = list()
        for index, row in enumerate(params['covariance']):
            covariance.append(row[:index + 1])

        params['covariance'] = covariance

        univariates = dict()
        for name, univariate in zip(params.pop('columns'), params['univariates']):
            univariates[name] = univariate
            if 'scale' in univariate:
                scale = univariate['scale']
                if scale == 0:
                    scale = copulas.EPSILON

                univariate['scale'] = np.log(scale)

        params['univariates'] = univariates
        params['num_rows'] = self._num_rows

        return flatten_dict(params)

    def _rebuild_covariance_matrix(self, covariance):
        """Rebuild the covariance matrix from its parameter values.

        This method follows the steps:

            * Rebuild a square matrix out of a triangular one.
            * Add the missing half of the matrix by adding its transposed and
              then removing the duplicated diagonal values.
            * ensure the matrix is positive definite

        Args:
            covariance (list):
                covariance values after unflattening model parameters.

        Result:
            list[list[float]]:
                Symmetric positive semi-definite matrix.
        """
        covariance = np.array(square_matrix(covariance))
        covariance = (covariance + covariance.T - (np.identity(covariance.shape[0]) * covariance))

        if not check_matrix_symmetric_positive_definite(covariance):
            covariance = make_positive_definite(covariance)

        return covariance.tolist()

    def _rebuild_gaussian_copula(self, model_parameters):
        """Rebuild the model params to recreate a Gaussian Multivariate instance.

        Args:
            model_parameters (dict):
                Sampled and reestructured model parameters.

        Returns:
            dict:
                Model parameters ready to recreate the model.
        """
        columns = list()
        univariates = list()
        for column, univariate in model_parameters['univariates'].items():
            columns.append(column)
            univariate['type'] = self._distribution[column]
            if 'scale' in univariate:
                univariate['scale'] = np.exp(univariate['scale'])

            univariates.append(univariate)

        model_parameters['univariates'] = univariates
        model_parameters['columns'] = columns

        covariance = model_parameters.get('covariance')
        model_parameters['covariance'] = self._rebuild_covariance_matrix(covariance)

        return model_parameters

    def set_parameters(self, parameters):
        """Set copula model parameters.

        Args:
            dict:
                Copula flatten parameters.
        """
        parameters = unflatten_dict(parameters)
        parameters = self._rebuild_gaussian_copula(parameters)

        num_rows = parameters.pop('num_rows')
        self._num_rows = 0 if pd.isnull(num_rows) else max(0, int(round(num_rows)))
        self._model = copulas.multivariate.GaussianMultivariate.from_dict(parameters)
