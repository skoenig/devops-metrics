import pytest
from unittest.mock import patch, MagicMock
import os
import datetime
from pipeline_metrics import pipeline_time, lead_time

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        "PROJECT_ID": "test-project",
        "BUILD_ID": "test-build",
        "REPO_PATH": "/test/repo",
        "TAG_NAME": "v1.0.0"
    }):
        yield

def test_pipeline_time(mock_env_vars):
    with patch('pipeline_metrics.CloudBuildClient') as mock_cloud_build_client:
        mock_build = MagicMock()
        mock_build.start_time = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
        mock_cloud_build_client.return_value.get_build.return_value = mock_build

        with patch('pipeline_metrics.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

            with patch('builtins.print') as mock_print:
                pipeline_time()
                mock_print.assert_called_with('pipeline_time: 3600.0')

def test_lead_time(mock_env_vars):
    with patch('pipeline_metrics.mk_run') as mock_mk_run:
        mock_run = MagicMock()
        mock_mk_run.return_value = mock_run

        with patch('pipeline_metrics.fetch_tags_and_author_dates') as mock_fetch_tags_and_author_dates:
            mock_fetch_tags_and_author_dates.return_value = [
                ('v1.0.0', 1672531200),  # 2023-01-01 00:00:00
            ]

            with patch('pipeline_metrics.datetime') as mock_datetime:
                mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

                with patch('builtins.print') as mock_print:
                    lead_time()
                    mock_print.assert_called_with('lead_time: 3600.000000')