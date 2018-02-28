from rest_framework.test import APITestCase

from helpers.deep import get_processed_data
from helpers.create_classifier import create_classifier_model
from classifier.models import ClassifiedDocument


class TestClassificationAPI(APITestCase):
    """
    Tests for text classification API
    """
    def setUp(self):
        self.classifier_model = self._get_model(version=1)
        self.classifier_model.save()
        # TODO: And create some classified docs as well
        self.classified_doc = ClassifiedDocument.objects.create(
            text="Sample text",
            classifier=self.classifier_model,
            confidence=0.2,
            classification_label="ABC",
            classification_probabilities=self.classifier_model.classifier.
                classify_as_label_probs("Sample text")
        )
        self.url = '/api/v1/classify/'

    def test_no_text_and_no_deeper_param(self):
        params = {}
        response = self.client.post(self.url, params)
        assert response.status_code == 400, "No params should be a bad request"
        data = response.json()
        assert 'text' in data

    def test_no_text_and_deeper_param(self):
        params = {'deeper': '1'}
        response = self.client.post(self.url, params)
        assert response.status_code == 400, "Should be a bad request"
        data = response.json()
        assert 'text' in data
        assert 'doc_id' in data

    def test_api_with_text(self):
        params = {'text': 'This is to be classified'}
        response = self.client.post(self.url, params)
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert "classification_confidence" in data
        assert type(data['classification']) == list
        # Just to check if list contains tuples, if not exception raised
        for label, prob in data['classification']:
            pass

    def test_api_with_text_deeper(self):
        params = {'text': 'This is to be classified', 'deeper': '1'}
        response = self.client.post(self.url, params)
        assert response.status_code == 200
        data = response.json()
        assert "group_id" in data
        assert "id" in data
        assert "classification" in data
        assert "classification_confidence" in data
        assert type(data['classification']) == list
        # Just to check if list contains tuples, if not exception raised
        for label, prob in data['classification']:
            pass
        assert 'excerpts_classification' in data
        for x in data['excerpts_classification']:
            assert 'start_pos' in x, "Start pos not in excerpt"
            assert 'end_pos' in x, "End pos not in excerpt"
            assert 'classification' in x, "classification not in excerpt"
            assert 'classification_confidence' in x, \
                "classification_confidence not in excerpt"

    def test_api_with_doc_id(self):
        params = {'doc_id': self.classified_doc.id, 'deeper': '1'}
        response = self.client.post(self.url, params)
        assert response.status_code == 200
        data = response.json()
        assert "group_id" in data
        assert "id" in data
        assert "classification" in data
        assert "classification_confidence" in data
        assert type(data['classification']) == list
        # Just to check if list contains tuples, if not exception raised
        for label, prob in data['classification']:
            pass
        assert 'excerpts_classification' in data
        for x in data['excerpts_classification']:
            assert 'start_pos' in x, "Start pos not in excerpt"
            assert 'end_pos' in x, "End pos not in excerpt"
            assert 'classification' in x, "classification not in excerpt"
            assert 'classification_confidence' in x, \
                "classification_confidence not in excerpt"

    def _get_model(self, version):
        # first create classifier
        csv_path = 'fixtures/processed_data_for_testing.csv'
        data = get_processed_data(csv_path)
        return create_classifier_model(version, data)

    def _create_classified_docs(self, classifier_model):
        classifier = classifier_model.classifier
        texts = []


def assertion_structure_data(structure, data):
    """
    Automatic checks if data matches structure
    """
    # TODO: fix this, currently errors
    print(structure)
    if type(structure) == dict:
        assert isinstance(data, dict)
        for k, v in structure.items():
            assert k in data
            assertion_structure_data(structure[k], data[k])
    elif type(structure) == list:
        assert isinstance(data, list)
        for x in data:
            assertion_structure_data(structure[0], x)
    elif type(structure) == tuple:
        assert len(structure) == len(data)
        for i, k in enumerate(data):
            assert isinstance(k, type(structure[i]))
    else:
        # primitive type
        assert isinstance(data, structure)
