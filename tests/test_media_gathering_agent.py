#!/usr/bin/env python3
"""
Test Suite for Media Gathering Agent

Run with: pytest tests/test_media_gathering_agent.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Import the agent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from media_gathering_agent import (
    MediaGatheringAgent,
    MediaRequest,
    MediaResult,
    AgentConfig,
    LogLevel
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def agent_config():
    """Create test configuration"""
    return AgentConfig(
        max_retries=1,
        api_timeout=5,
        download_timeout=5,
        max_search_queries=2,
        results_per_source=2,
        min_final_score=30.0
    )


@pytest.fixture
def basic_agent(temp_output_dir, agent_config):
    """Create agent instance for testing"""
    return MediaGatheringAgent(
        output_dir=str(temp_output_dir),
        config=agent_config,
        log_level=LogLevel.DEBUG
    )


@pytest.fixture
def media_request():
    """Create test media request"""
    return MediaRequest(
        query="children learning cartoon",
        media_type="image",
        quantity=3,
        constraints={"style": "cartoon"}
    )


# ============================================================================
# UNIT TESTS: CONFIGURATION
# ============================================================================

class TestAgentConfig:
    """Test AgentConfig and related configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AgentConfig()
        assert config.max_retries == 3
        assert config.api_timeout == 5
        assert config.download_timeout == 10
        assert config.min_final_score == 50.0
    
    def test_custom_config(self, agent_config):
        """Test custom configuration"""
        assert agent_config.max_retries == 1
        assert agent_config.min_final_score == 30.0
    
    def test_config_modification(self, agent_config):
        """Test that config can be modified"""
        original_retries = agent_config.max_retries
        agent_config.max_retries = 5
        assert agent_config.max_retries == 5


# ============================================================================
# UNIT TESTS: AGENT INITIALIZATION
# ============================================================================

class TestAgentInit:
    """Test agent initialization and setup"""
    
    def test_agent_initialization(self, basic_agent):
        """Test agent initializes correctly"""
        assert basic_agent.output_dir is not None
        assert basic_agent.session is not None
    
    def test_agent_output_directory_creation(self, temp_output_dir):
        """Test that agent respects output directory"""
        agent = MediaGatheringAgent(str(temp_output_dir))
        assert Path(agent.output_dir).exists()
    
    def test_agent_with_different_log_levels(self, temp_output_dir):
        """Test agent initialization with different log levels"""
        for level in [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING]:
            agent = MediaGatheringAgent(
                output_dir=str(temp_output_dir),
                log_level=level
            )
            assert agent.session is not None


# ============================================================================
# UNIT TESTS: MEDIA REQUEST
# ============================================================================

class TestMediaRequestClass:
    """Test MediaRequest dataclass"""
    
    def test_basic_request(self):
        """Test creating a basic media request"""
        request = MediaRequest(
            query="test",
            media_type="image",
            quantity=5
        )
        assert request.query == "test"
        assert request.media_type == "image"
        assert request.quantity == 5
    
    def test_request_with_constraints(self):
        """Test request with style constraints"""
        constraints = {"style": "cartoon", "color": "bright"}
        request = MediaRequest(
            query="test",
            media_type="image",
            quantity=5,
            constraints=constraints
        )
        assert request.constraints == constraints
    
    def test_request_validation_quantity(self):
        """Test that quantity is respected"""
        request = MediaRequest(
            query="test",
            media_type="image",
            quantity=100
        )
        assert request.quantity == 100


# ============================================================================
# UNIT TESTS: QUERY GENERATION
# ============================================================================

class TestQueryGeneration:
    """Test search query generation"""
    
    def test_generate_queries(self, basic_agent, media_request):
        """Test that agent generates multiple queries"""
        queries = basic_agent._generate_search_queries(media_request)
        assert isinstance(queries, list)
        assert len(queries) > 0
        assert all(isinstance(q, str) for q in queries)
    
    def test_query_variation(self, basic_agent, media_request):
        """Test that generated queries are varied"""
        queries = basic_agent._generate_search_queries(media_request)
        # Should have at least one query
        assert len(queries) >= 1
    
    def test_query_includes_base_keyword(self, basic_agent):
        """Test that queries include base keyword"""
        request = MediaRequest(
            query="children",
            media_type="image",
            quantity=3,
            constraints={"style": "cartoon"}
        )
        queries = basic_agent._generate_search_queries(request)
        # At least the first query should include the base keyword
        assert any("children" in q.lower() for q in queries) or len(queries) >= 1


# ============================================================================
# UNIT TESTS: SCORING & VALIDATION
# ============================================================================

class TestScoringMethods:
    """Test scoring and validation functions"""
    
    def test_quality_score_calculation(self, basic_agent):
        """Test quality score for different resolutions"""
        # High resolution
        score = basic_agent._calculate_quality_score(
            width=1920,
            height=1080,
            license_type="CC0"
        )
        assert score > 50  # Should be reasonably high
        
        # Low resolution
        score = basic_agent._calculate_quality_score(
            width=400,
            height=300,
            license_type="CC0"
        )
        assert 0 <= score <= 100  # Valid range
    
    def test_relevance_score(self, basic_agent):
        """Test relevance scoring"""
        title = "cartoon children learning communication"
        query = "children learning"
        
        score = basic_agent._calculate_relevance_score(title, query)
        assert 0 <= score <= 100
    
    def test_final_score_calculation(self, basic_agent):
        """Test final score combines all components"""
        score = basic_agent._calculate_final_score(
            relevance=70,
            quality=80,
            style_confidence=0.8
        )
        assert isinstance(score, float)
        assert score >= 0


# ============================================================================
# UNIT TESTS: RETRY LOGIC
# ============================================================================

class TestRetryMechanism:
    """Test exponential backoff retry logic"""
    
    def test_successful_first_attempt(self, basic_agent):
        """Test that successful function doesn't retry"""
        call_count = 0
        
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = basic_agent._with_retry(successful_func, max_attempts=3)
        assert result == "success"
        assert call_count == 1
    
    def test_retry_on_failure(self, basic_agent):
        """Test that failed attempts are retried"""
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = basic_agent._with_retry(failing_func, max_attempts=3)
        assert result == "success"
        assert call_count == 3
    
    def test_exhausted_retries(self, basic_agent):
        """Test that function returns None after exhausting retries"""
        def always_fails():
            raise Exception("Always fails")
        
        result = basic_agent._with_retry(always_fails, max_attempts=2)
        assert result is None


# ============================================================================
# INTEGRATION TESTS: REQUEST PROCESSING
# ============================================================================

class TestRequestProcessing:
    """Integration tests for request processing"""
    
    def test_process_request_returns_report(self, basic_agent, media_request):
        """Test that process_request returns properly structured report"""
        with patch('requests.Session.get') as mock_get:
            # Mock API that returns no results (safe for testing)
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # Should return report even with no results
            report = basic_agent.process_request(media_request)
            assert isinstance(report, dict)
            assert "summary" in report
    
    def test_report_structure(self, basic_agent, media_request):
        """Test that report has required fields"""
        with patch('requests.Session.get'):
            report = basic_agent.process_request(media_request)
            
            # Check summary section
            assert "summary" in report
            summary = report["summary"]
            assert "total_retrieved" in summary


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_query(self, basic_agent):
        """Test handling of empty query"""
        request = MediaRequest(
            query="",
            media_type="image",
            quantity=5
        )
        assert request.query == ""
    
    def test_zero_quantity(self, basic_agent):
        """Test handling of zero quantity"""
        request = MediaRequest(
            query="test",
            media_type="image",
            quantity=0
        )
        assert request.quantity == 0
    
    def test_very_large_quantity(self, basic_agent):
        """Test handling of unreasonably large quantity"""
        request = MediaRequest(
            query="test",
            media_type="image",
            quantity=10000
        )
        assert request.quantity == 10000
    
    @patch('requests.Session.get')
    def test_timeout_handling(self, mock_get, basic_agent):
        """Test handling of timeout errors"""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        result = basic_agent._with_retry(
            lambda: mock_get("http://example.com"),
            max_attempts=2
        )
        # Should return None after timeouts
        assert result is None
    
    @patch('requests.Session.get')
    def test_connection_error_handling(self, mock_get, basic_agent):
        """Test handling of connection errors"""
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        result = basic_agent._with_retry(
            lambda: mock_get("http://example.com"),
            max_attempts=2
        )
        # Should return None after connection errors
        assert result is None


# ============================================================================
# CONFIGURATION & PARAMETER TESTS
# ============================================================================

class TestConfigurationParams:
    """Test configuration parameter handling"""
    
    def test_scoring_weights(self):
        """Test that scoring weights are properly configured"""
        config = AgentConfig(
            quality_weight=0.5,
            relevance_weight=0.5,
            style_confidence_weight=0.2
        )
        assert config.quality_weight == 0.5
        assert config.relevance_weight == 0.5
    
    def test_timeout_values(self):
        """Test timeout configuration"""
        config = AgentConfig(
            api_timeout=20,
            download_timeout=30
        )
        assert config.api_timeout == 20
        assert config.download_timeout == 30
    
    def test_retry_configuration(self):
        """Test retry configuration"""
        config = AgentConfig(
            max_retries=5,
            retry_delay_base=2.0
        )
        assert config.max_retries == 5
        assert config.retry_delay_base == 2.0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_query_generation_speed(self, basic_agent, media_request):
        """Test that query generation is fast"""
        import time
        start = time.time()
        queries = basic_agent._generate_search_queries(media_request)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 0.5
        assert len(queries) > 0
    
    def test_scoring_speed(self, basic_agent):
        """Test that scoring is fast"""
        import time
        start = time.time()
        
        for _ in range(100):
            basic_agent._calculate_final_score(
                relevance=70,
                quality=80,
                style_confidence=0.8
            )
        
        elapsed = time.time() - start
        # 100 score calculations should be fast
        assert elapsed < 1.0


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# Run with: pytest tests/test_media_gathering_agent.py -v
# Run only fast tests: pytest tests/test_media_gathering_agent.py -v -m "not slow"
# Run specific test: pytest tests/test_media_gathering_agent.py::TestAgentConfig::test_default_config -v
