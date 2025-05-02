import pytest
from httpx import AsyncClient
from src.weather_api import make_nws_request, get_alerts

@pytest.mark.asyncio
async def test_make_nws_request_success(mocker):
    mock_response = {"features": []}
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
    
    url = "https://api.weather.gov/alerts/active/area/CA"
    response = await make_nws_request(url)
    
    assert response == mock_response

@pytest.mark.asyncio
async def test_make_nws_request_failure(mocker):
    mocker.patch("httpx.AsyncClient.get", side_effect=Exception("Network error"))
    
    url = "https://api.weather.gov/alerts/active/area/CA"
    response = await make_nws_request(url)
    
    assert response is None

@pytest.mark.asyncio
async def test_get_alerts_no_data(mocker):
    mocker.patch("src.weather_api.make_nws_request", return_value=None)
    
    state = "CA"
    response = await get_alerts(state)
    
    assert response == "Unable to fetch alerts or no alerts found."

@pytest.mark.asyncio
async def test_get_alerts_no_features(mocker):
    mock_response = {"features": []}
    mocker.patch("src.weather_api.make_nws_request", return_value=mock_response)
    
    state = "CA"
    response = await get_alerts(state)
    
    assert response == "No active alerts for this state."

@pytest.mark.asyncio
async def test_get_alerts_with_features(mocker):
    mock_response = {
        "features": [
            {"properties": {"headline": "Alert 1"}},
            {"properties": {"headline": "Alert 2"}},
        ]
    }
    mocker.patch("src.weather_api.make_nws_request", return_value=mock_response)
    
    state = "CA"
    response = await get_alerts(state)
    
    assert response == "Alert 1\n---\nAlert 2"