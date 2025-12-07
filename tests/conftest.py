#!/usr/bin/env python3
"""
Pytest fixtures and configuration for Media Gathering Agent tests

Provides shared fixtures for:
- Temporary directories
- Agent instances
- Mock API responses
- Common test data
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from media_gathering_agent import (
    MediaGatheringAgent,
    MediaRequest,
    MediaResult,
    AgentConfig,
    LogLevel,
    setup_logger
)


# ============================================================================
# DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_output_dir():
    """Create and provide temporary output directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def media_dir_structure(temp_output_dir):
    """Create media directory structure for testing"""
    media_dir = temp_output_dir / "media"
    media_dir.mkdir(exist_ok=True)
    (media_dir / "handout_1_slp_info").mkdir(exist_ok=True)
    (media_dir / "handout_2_communication_strategies").mkdir(exist_ok=True)
    (media_dir / "handout_3_ontario_resources").mkdir(exist_ok=True)
    return media_dir


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def default_config():
    """Provide default agent configuration"""
    return AgentConfig()


@pytest.fixture
def test_config():
    """Provide test-optimized configuration"""
    return AgentConfig(
        max_retries=1,
        api_timeout=5,
        download_timeout=5,
        max_search_queries=2,
        results_per_source=2,
        min_final_score=30.0,
        retry_delay_base=0.1  # Fast retries for testing
    )


@pytest.fixture
def strict_config():
    """Provide strict configuration for validation tests"""
    return AgentConfig(
        min_final_score=70.0,
        quality_weight=0.5,
        relevance_weight=0.5,
        style_confidence_weight=0.3
    )


# ============================================================================
# AGENT FIXTURES
# ============================================================================

@pytest.fixture
def basic_agent(temp_output_dir, test_config):
    """Create agent instance with test configuration"""
    return MediaGatheringAgent(
        output_dir=str(temp_output_dir),
        config=test_config,
        log_level=LogLevel.DEBUG
    )


@pytest.fixture
def default_agent(temp_output_dir):
    """Create agent instance with default configuration"""
    return MediaGatheringAgent(
        output_dir=str(temp_output_dir),
        log_level=LogLevel.WARNING
    )


@pytest.fixture
def strict_agent(temp_output_dir, strict_config):
    """Create agent instance with strict scoring configuration"""
    return MediaGatheringAgent(
        output_dir=str(temp_output_dir),
        config=strict_config,
        log_level=LogLevel.WARNING
    )


# ============================================================================
# MEDIA REQUEST FIXTURES
# ============================================================================

@pytest.fixture
def cartoon_request():
    """Create cartoon media request"""
    return MediaRequest(
        query="children learning with teacher in classroom cartoon",
        media_type="image",
        quantity=3,
        quality="professional",
        licensing="free",
        context={"handout": "1_slp_info"},
        constraints={"style": "cartoon"}
    )


@pytest.fixture
def photo_request():
    """Create photo media request"""
    return MediaRequest(
        query="children communication therapy real people",
        media_type="image",
        quantity=2,
        quality="high",
        licensing="free",
        context={"handout": "2_communication_strategies"},
        constraints={"style": "photo"}
    )


@pytest.fixture
def no_style_request():
    """Create media request with no style constraint"""
    return MediaRequest(
        query="autism awareness education",
        media_type="image",
        quantity=2,
        quality="medium",
        licensing="free",
        context={"handout": "3_ontario_resources"},
        constraints={}
    )


@pytest.fixture
def video_request():
    """Create video media request"""
    return MediaRequest(
        query="children learning video educational",
        media_type="video",
        quantity=1,
        quality="high",
        licensing="free",
        context={"handout": "1_slp_info"},
        constraints={"style": "photo"}
    )


# ============================================================================
# MOCK RESPONSE FIXTURES
# ============================================================================

def create_unsplash_mock_response(query: str, count: int = 2) -> Mock:
    """Create mock Unsplash API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "id": f"unsplash_id_{i}",
                "urls": {
                    "regular": f"https://unsplash.com/image_{i}.jpg"
                },
                "description": f"Cartoon image {i} - {query}",
                "width": 1920,
                "height": 1080,
                "user": {
                    "name": f"Photographer {i}"
                },
                "tags": [
                    {"title": "cartoon"},
                    {"title": "illustration"},
                    {"title": "educational"}
                ]
            }
            for i in range(count)
        ]
    }
    return mock_response


def create_pexels_image_mock_response(query: str, count: int = 2) -> Mock:
    """Create mock Pexels image API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "photos": [
            {
                "id": f"pexels_img_{i}",
                "src": {
                    "original": f"https://pexels.com/image_{i}.jpg"
                },
                "width": 1280,
                "height": 720,
                "photographer": f"Photographer {i}",
                "photographer_url": f"https://pexels.com/photographer_{i}"
            }
            for i in range(count)
        ]
    }
    return mock_response


def create_pexels_video_mock_response(query: str, count: int = 1) -> Mock:
    """Create mock Pexels video API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "videos": [
            {
                "id": f"pexels_vid_{i}",
                "video_files": [
                    {
                        "link": f"https://pexels.com/video_{i}.mp4"
                    }
                ],
                "duration": 30,
                "width": 1920,
                "height": 1080
            }
            for i in range(count)
        ]
    }
    return mock_response


def create_error_response(status_code: int) -> Mock:
    """Create mock error response"""
    mock_response = Mock()
    mock_response.status_code = status_code
    return mock_response


def create_timeout_error():
    """Create mock timeout error"""
    import requests
    error = requests.Timeout("Connection timeout")
    return error


def create_connection_error():
    """Create mock connection error"""
    import requests
    error = requests.ConnectionError("Connection failed")
    return error


@pytest.fixture
def mock_unsplash_success():
    """Mock successful Unsplash API response"""
    return create_unsplash_mock_response("cartoon", count=2)


@pytest.fixture
def mock_pexels_image_success():
    """Mock successful Pexels image API response"""
    return create_pexels_image_mock_response("photo", count=2)


@pytest.fixture
def mock_pexels_video_success():
    """Mock successful Pexels video API response"""
    return create_pexels_video_mock_response("educational", count=1)


@pytest.fixture
def mock_401_unauthorized():
    """Mock 401 Unauthorized response"""
    return create_error_response(401)


@pytest.fixture
def mock_403_forbidden():
    """Mock 403 Forbidden response"""
    return create_error_response(403)


@pytest.fixture
def mock_500_server_error():
    """Mock 500 Server Error response"""
    return create_error_response(500)


@pytest.fixture
def mock_timeout():
    """Mock timeout error"""
    return create_timeout_error()


@pytest.fixture
def mock_connection_error():
    """Mock connection error"""
    return create_connection_error()


# ============================================================================
# CANDIDATE/MEDIA FIXTURES
# ============================================================================

def create_cartoon_candidate(
    id: str = "unsplash_cartoon_001",
    resolution: str = "1920x1080"
) -> Dict:
    """Create mock cartoon media candidate"""
    return {
        "id": id,
        "url": "https://example.com/cartoon.jpg",
        "title": "Cartoon illustration of children learning",
        "source": "unsplash",
        "license": "cc0",
        "resolution": resolution,
        "metadata": {
            "photographer": "Test Photographer",
            "description": "Cartoon style illustration with children",
            "tags": ["cartoon", "illustration", "children", "learning"]
        }
    }


def create_photo_candidate(
    id: str = "pexels_photo_001",
    resolution: str = "1280x720"
) -> Dict:
    """Create mock photo media candidate"""
    return {
        "id": id,
        "url": "https://example.com/photo.jpg",
        "title": "Professional photograph of children in classroom",
        "source": "pexels",
        "license": "free-commercial",
        "resolution": resolution,
        "metadata": {
            "photographer": "Test Photographer",
            "description": "Real photograph of people",
            "tags": ["photo", "children", "classroom", "real"]
        }
    }


def create_low_quality_candidate() -> Dict:
    """Create low-quality media candidate"""
    return {
        "id": "low_quality_001",
        "url": "https://example.com/low.jpg",
        "title": "Low res image",
        "source": "unknown",
        "license": "unknown",
        "resolution": "400x300",
        "metadata": {}
    }


def create_irrelevant_candidate() -> Dict:
    """Create irrelevant media candidate"""
    return {
        "id": "irrelevant_001",
        "url": "https://example.com/irrelevant.jpg",
        "title": "Landscape sunset",
        "source": "unsplash",
        "license": "cc0",
        "resolution": "1920x1080",
        "metadata": {
            "description": "Beautiful sunset landscape",
            "tags": ["nature", "sunset", "landscape"]
        }
    }


@pytest.fixture
def cartoon_candidate():
    """Provide cartoon candidate"""
    return create_cartoon_candidate()


@pytest.fixture
def photo_candidate():
    """Provide photo candidate"""
    return create_photo_candidate()


@pytest.fixture
def low_quality_candidate():
    """Provide low-quality candidate"""
    return create_low_quality_candidate()


@pytest.fixture
def irrelevant_candidate():
    """Provide irrelevant candidate"""
    return create_irrelevant_candidate()


@pytest.fixture
def candidate_list():
    """Provide list of mixed candidates"""
    return [
        create_cartoon_candidate("cand_001", "1920x1080"),
        create_cartoon_candidate("cand_002", "1280x720"),
        create_photo_candidate("cand_003", "1024x768"),
        create_low_quality_candidate(),
        create_irrelevant_candidate()
    ]


# ============================================================================
# MEDIA RESULT FIXTURES
# ============================================================================

def create_media_result(
    id: str = "result_001",
    quality_score: float = 80.0,
    relevance_score: float = 75.0,
    style_confidence: float = 0.9
) -> MediaResult:
    """Create mock media result"""
    return MediaResult(
        id=id,
        url="https://example.com/media.jpg",
        local_path=f"/tmp/media/{id}.jpg",
        title="Test Media Result",
        license="cc0",
        source="test",
        media_type="image",
        resolution="1920x1080",
        file_size=512000,
        quality_score=quality_score,
        relevance_score=relevance_score,
        style_confidence=style_confidence,
        final_score=(
            (relevance_score * 0.6 + quality_score * 0.4) +
            (style_confidence * 100.0 * 0.2)
        ),
        metadata={"test": "data"}
    )


@pytest.fixture
def media_result():
    """Provide media result"""
    return create_media_result()


@pytest.fixture
def media_result_list():
    """Provide list of media results"""
    return [
        create_media_result("result_001", 85.0, 80.0, 0.95),
        create_media_result("result_002", 75.0, 70.0, 0.80),
        create_media_result("result_003", 65.0, 60.0, 0.70)
    ]


# ============================================================================
# MOCK SESSION FIXTURES
# ============================================================================

@pytest.fixture
def mock_session():
    """Create mock requests Session"""
    session = MagicMock()
    session.headers = {}
    return session


# ============================================================================
# REPORT FIXTURES
# ============================================================================

def create_mock_report(
    total_requested: int = 5,
    total_retrieved: int = 3,
    quality_avg: float = 75.0,
    relevance_avg: float = 70.0,
    style_confidence_avg: float = 0.8,
    final_score_avg: float = 65.0
) -> Dict:
    """Create mock report"""
    return {
        "request_id": "test-request-123",
        "timestamp": "2024-01-01T00:00:00",
        "status": "success" if total_retrieved > 0 else "partial",
        "request": {
            "query": "test query",
            "media_type": "image",
            "quantity": total_requested
        },
        "results": [create_media_result() for _ in range(total_retrieved)],
        "summary": {
            "total_requested": total_requested,
            "total_retrieved": total_retrieved,
            "retrieval_rate": f"{(total_retrieved/total_requested*100):.0f}%",
            "quality_avg": f"{quality_avg:.1f}",
            "relevance_avg": f"{relevance_avg:.1f}",
            "style_confidence_avg": f"{style_confidence_avg:.2f}",
            "final_score_avg": f"{final_score_avg:.1f}"
        }
    }


@pytest.fixture
def mock_report():
    """Provide mock report"""
    return create_mock_report()


@pytest.fixture
def mock_partial_report():
    """Provide mock partial report (partial success)"""
    return create_mock_report(total_requested=5, total_retrieved=1)


@pytest.fixture
def mock_empty_report():
    """Provide mock empty report (no results)"""
    return create_mock_report(total_requested=5, total_retrieved=0)


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "mock: marks tests that use mocking"
    )
    config.addinivalue_line(
        "markers", "retry: marks tests for retry logic"
    )
    config.addinivalue_line(
        "markers", "scoring: marks tests for scoring logic"
    )
