from rest_framework.test import APITestCase
from django.conf import settings

from classifier.models import ClassifiedDocument
from clustering.tasks import create_new_clusters
from clustering.models import ClusteringModel

from api.tests.utils import with_token_auth_tests

import os


@with_token_auth_tests
class TestClusteringAPI(APITestCase):
    """
    Tests for clustering API
    """
    fixtures = [
        'fixtures/classifier.json',
        'fixtures/test_classified_docs.json',
        'fixtures/test_base_models.json',
    ]

    def setUp(self):
        # first create clusters
        self.cluster_data_path = 'test_clusters/'
        # create path if not exist
        os.system('mkdir -p {}'.format(self.cluster_data_path))
        os.environ[settings.ENVIRON_CLUSTERING_DATA_LOCATION] = \
            self.cluster_data_path
        # set values
        self.group_id = '1'
        self.num_clusters = 2
        self.api_url = '/api/cluster/'
        self.valid_params = {
            'group_id': self.group_id,
            'num_clusters': self.num_clusters
        }
        # this creates token and adds that to client header
        super().setUp()

    def test_no_group_id(self):
        params = {}
        response = self.client.post(self.api_url, params)
        assert response.status_code == 400, "No group_id is a bad request."
        data = response.json()
        assert 'group_id' in data

    def test_invalid_num_clusters(self):
        params = {'group_id': '1'}
        invalids = [None, 'abc', '  ', 'bibek', 1.1, -3, '1.10']
        for invalid in invalids:
            if invalids is not None:
                params['num_clusters'] = invalid
            response = self.client.post(self.api_url, params)
            assert response.status_code == 400,\
                "No num_clusters is a bad request."
            data = response.json()
            assert 'num_clusters' in data

    def test_no_docs_with_group_id(self):
        params = {'group_id': 'not existing', 'num_clusters': 5}
        response = self.client.post(self.api_url, params)
        data = response.json()
        assert response.status_code == 400, "If no docs, it is a bad request"
        data = response.json()
        assert 'message' in data

    def test_create_cluster_first_request_api(self):
        """Test when cluster_create request is sent"""
        params = self.valid_params
        response = self.client.post(self.api_url, params)
        data = response.json()
        assert response.status_code == 202, "No data returned but accepted"
        data = response.json()
        assert 'cluster_model_id' in data

    def test_clustered_prepared_resposne(self):
        # create a clustered model
        cluster_model = create_new_clusters(
            "test_cluster", self.group_id, 2
        )
        params = self.valid_params
        response = self.client.post(self.api_url, params)
        assert response.status_code == 201
        data = response.json()
        assert 'cluster_model_id' in data
        assert isinstance(data['cluster_model_id'], int)
        assert data['cluster_model_id'] == cluster_model.id

    def test_get_cluster_invalid_model_id(self):
        params = {}
        invalids = [None, "abcd", "1.1", "-1"]
        for invalid in invalids:
            if invalid is not None:
                params['cluster_model_id'] = invalid
            response = self.client.get(self.api_url, params)
            assert response.status_code == 400, "no model_id should be 400"
            data = response.json()
            assert 'cluster_model_id' in data

    def test_get_cluster_non_existent_model_id(self):
        params = {'cluster_model_id': 9876543}
        response = self.client.get(self.api_url, params)
        assert response.status_code == 404, "non existent cluster_model_id is 404"  # noqa
        data = response.json()
        assert 'message' in data

    def test_get_cluster(self):
        cluster_model = create_new_clusters(
            "test_cluster", self.group_id, 2
        )
        params = {'cluster_model_id': cluster_model.id}
        response = self.client.get(self.api_url, params)
        assert response.status_code == 200
        data = response.json()
        assert 'score' in data
        assert data['score'] >= -1 and data['score'] <= 1
        assert 'doc_ids' in data
        assert isinstance(data['doc_ids'], list)
        for did in data['doc_ids']:
            isinstance(did, int)
        assert 'relevant_terms' in data
        for term in data['relevant_terms']:
            assert isinstance(term, str)
        assert 'group_id' in data
        assert isinstance(data['group_id'], str)

    def tearDown(self):
        # remove test cluster folder
        os.system('rm -r {}'.format(self.cluster_data_path))


@with_token_auth_tests
class TestReClusteringAPI(APITestCase):
    """Tests for re-clustering"""
    fixtures = [
        'fixtures/classifier.json',
        'fixtures/test_classified_docs.json',
        'fixtures/test_base_models.json',
    ]

    def setUp(self):
        self.cluster_data_path = 'test_clusters/'
        # create path if not exist
        os.system('mkdir -p {}'.format(self.cluster_data_path))
        os.environ[settings.ENVIRON_CLUSTERING_DATA_LOCATION] = \
            self.cluster_data_path
        # set values
        self.group_id = '1'
        self.num_clusters = 2
        self.url = '/api/re-cluster/'
        self.valid_params = {
            'group_id': self.group_id,
            'num_clusters': self.num_clusters
        }
        self.cluster_model = create_new_clusters(
            "test_cluster", self.group_id, self.num_clusters
        )
        # this creates token and adds that to client header
        super().setUp()

    def test_no_params(self):
        params = {}
        resp = self.client.post(self.url, params)
        assert resp.status_code == 400
        data = resp.json()
        assert 'group_id' in data
        assert 'num_clusters' in data

    def test_no_group_id(self):
        params = {'num_clusters': 3}
        resp = self.client.post(self.url, params)
        assert resp.status_code == 400
        data = resp.json()
        assert 'group_id' in data

    def test_no_num_clusters(self):
        params = {'group_id': '1'}
        resp = self.client.post(self.url, params)
        assert resp.status_code == 400
        data = resp.json()
        assert 'num_clusters' in data

    def test_non_existent_cluster(self):
        """Cluster with group id does not exist"""
        params = self.valid_params
        params['group_id'] = 'does not exist'
        resp = self.client.post(self.url, params)
        assert resp.status_code == 404
        data = resp.json()
        assert 'message' in data

    def test_not_ready_cluster(self):
        """The cluster is not yet finished running"""
        # first set ready = False
        self.cluster_model.ready = False
        self.cluster_model.save()
        resp = self.client.post(self.url, self.valid_params)
        assert resp.status_code == 202, "If not ready, accepted response"

    def test_recluster(self):
        # first set ready true, which will then be resent for clustering
        self.cluster_model.ready = True
        self.cluster_model.save()
        resp = self.client.post(self.url, self.valid_params)
        assert resp.status_code == 202, "If sent for reclustering, accepted response"  # noqa
        # check ready status of our clustering model, should be false
        assert not ClusteringModel.objects.get(id=self.cluster_model.id).ready

    def tearDown(self):
        # remove test cluster folder
        os.system('rm -r {}'.format(self.cluster_data_path))


@with_token_auth_tests
class TestClusteringDataAPI(APITestCase):
    """Tests for clustering data"""
    fixtures = [
        'fixtures/classifier.json',
        'fixtures/test_classified_docs.json',
        'fixtures/test_base_models.json',
    ]

    def setUp(self):
        self.cluster_data_path = 'test_clusters/'
        self.classified_doc = ClassifiedDocument.objects.last()
        self.classifier = self.classified_doc.classifier
        # create path if not exist
        os.system('mkdir -p {}'.format(self.cluster_data_path))
        os.environ[settings.ENVIRON_CLUSTERING_DATA_LOCATION] = \
            self.cluster_data_path
        self.group_id = self.classified_doc.group_id
        self.num_clusters = 2
        self.url = '/api/cluster-data/'

    def test_post(self):
        resp = self.client.post(self.url, {})
        assert resp.status_code == 405

    def test_no_model_id(self):
        resp = self.client.get(self.url, {})
        assert resp.status_code == 400
        data = resp.json()
        assert 'cluster_model_id' in data

    def test_cluster_data_not_ready(self):
        # remove all clusters
        ClusteringModel.objects.all().delete()
        # create one and set ready false
        cluster_model = create_new_clusters(
            "test", self.group_id, self.num_clusters
        )
        cluster_model.ready = False
        cluster_model.save()
        params = {'cluster_model_id': cluster_model.id}
        resp = self.client.get(self.url, params)
        assert resp.status_code == 202
        data = resp.json()
        assert 'message' in data

    def test_cluster_data_fully_clustered(self):
        """Test by sending valid data"""
        # Remove clusters
        ClusteringModel.objects.all().delete()
        # first create a cluster
        cluster_model = create_new_clusters(
            "test", self.group_id, self.num_clusters
        )
        params = {'cluster_model_id': cluster_model.id}
        resp = self.client.get(self.url, params)
        assert resp.status_code == 200
        data = resp.json()
        assert 'full_clustered' in data
        assert data['full_clustered'], "Recently created model should be fully clustered"  # noqa
        assert isinstance(data, dict)
        assert 'keywords' in data
        assert 'docs' in data
        assert isinstance(data['docs'], dict)
        for entry in data['keywords']:
            assert isinstance(entry, dict)
            assert 'cluster' in entry
            assert 'score' in entry
            assert 'value' in entry
        for label, docs in data['docs'].items():
            assert isinstance(docs, list)
            assert docs, "Docs should not be empty for a cluster"
            for docid in docs:
                assert isinstance(docid, int)

    def test_cluster_data_not_fully_clustered(self):
        """Test by sending valid data"""
        # Remove clusters
        ClusteringModel.objects.all().delete()
        # first create a cluster
        cluster_model = create_new_clusters(
            "test", self.group_id, self.num_clusters
        )
        # add a classifed doc
        ClassifiedDocument.objects.create(
            text="test test test",
            group_id=self.group_id,
            classifier=self.classifier
        )
        params = {'cluster_model_id': cluster_model.id}
        resp = self.client.get(self.url, params)
        assert resp.status_code == 200
        data = resp.json()
        assert 'keywords' in data
        assert 'docs' in data
        assert 'full_clustered' in data
        assert not data['full_clustered'], "If doc is added, model should not be fully clustered"  # noqa
        assert isinstance(data['keywords'], list)
        for entry in data['keywords']:
            assert isinstance(entry, dict)
            assert 'cluster' in entry
            assert 'score' in entry
            assert 'value' in entry


    def tearDown(self):
        # remove test cluster folder
        os.system('rm -r {}'.format(self.cluster_data_path))
