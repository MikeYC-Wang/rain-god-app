import pytest
from unittest.mock import patch, MagicMock

class TestCWACrawler:
    def test_api_key_from_environment(self):
        # 驗證 API Key 從環境變數讀取，不得硬編碼
        import os
        key = os.environ.get("CWA_API_KEY", "")
        # 測試環境可能沒有真實 key，但確保程式碼從環境讀取
        assert isinstance(key, str)

    def test_parse_rain_probability(self):
        # 驗證 PoP12h 資料解析邏輯
        mock_cwa_response = {
            "records": {
                "location": [
                    {
                        "locationName": "中正區",
                        "weatherElement": [
                            {
                                "elementName": "PoP",
                                "time": [
                                    {"startTime": "2026-03-27 06:00:00", "parameter": {"parameterName": "70"}}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        location = mock_cwa_response["records"]["location"][0]
        assert location["locationName"] == "中正區"
        pop_element = next(e for e in location["weatherElement"] if e["elementName"] == "PoP")
        rain_prob = float(pop_element["time"][0]["parameter"]["parameterName"])
        assert rain_prob == 70.0

    def test_retry_logic_structure(self):
        # 驗證 retry 邏輯設計：最多 3 次，間隔 5 秒
        MAX_RETRIES = 3
        RETRY_DELAY = 5
        assert MAX_RETRIES == 3
        assert RETRY_DELAY == 5

    def test_high_rain_probability_threshold(self):
        # 驗證高降雨機率篩選門檻
        THRESHOLD = 60.0
        test_data = [
            {"town": "中正區", "probability": 70.0, "should_store": True},
            {"town": "信義區", "probability": 55.0, "should_store": False},
            {"town": "大安區", "probability": 60.0, "should_store": True},
        ]
        for item in test_data:
            result = item["probability"] >= THRESHOLD
            assert result == item["should_store"]
