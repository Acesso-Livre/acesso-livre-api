from unittest.mock import MagicMock

import pytest

from acesso_livre_api.src.locations.service import update_location_average_rating


def test_update_location_average_rating_first_comment():
    mock_db = MagicMock()
    mock_location = MagicMock()
    mock_location.avg_rating = None
    mock_db.query().filter().first.return_value = mock_location
    mock_db.query().filter().count.return_value = 1
    result = update_location_average_rating(mock_db, location_id=1, new_value=5.0)
    assert mock_location.avg_rating == 5.0
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_location_average_rating_additional_comment():
    mock_db = MagicMock()
    mock_location = MagicMock()
    mock_location.avg_rating = 4.0
    mock_db.query().filter().first.return_value = mock_location
    mock_db.query().filter().count.return_value = 2
    result = update_location_average_rating(mock_db, location_id=1, new_value=5.0)
    assert abs(mock_location.avg_rating - 4.5) < 0.001
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_location_average_rating_location_not_found():
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    result = update_location_average_rating(mock_db, location_id=999, new_value=5.0)
    assert result is None
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


def test_update_location_average_rating_handling_none_avg():
    mock_db = MagicMock()
    mock_location = MagicMock()
    mock_location.avg_rating = None
    mock_db.query().filter().first.return_value = mock_location
    mock_db.query().filter().count.return_value = 1
    result = update_location_average_rating(mock_db, location_id=1, new_value=3.0)
    assert mock_location.avg_rating == 3.0
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_location_average_rating_db_error():
    mock_db = MagicMock()
    mock_location = MagicMock()
    mock_location.avg_rating = 4.0
    mock_db.query().filter().first.return_value = mock_location
    mock_db.query().filter().count.return_value = 1
    mock_db.commit.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        update_location_average_rating(mock_db, location_id=1, new_value=5.0)
