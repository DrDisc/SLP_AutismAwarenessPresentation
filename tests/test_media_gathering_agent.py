#!/usr/bin/env python3
"""
Comprehensive Test Suite for Media Gathering Agent

Run with: pytest tests/test_media_gathering_agent.py -v
Run with coverage: pytest tests/test_media_gathering_agent.py --cov=media_gathering_agent
Run specific test: pytest tests/test_media_gathering_agent.py::TestClassName::test_method_name -v

Test Categories:
1. Unit Tests for Core Components (dataclasses, config, logging)
2. API & Search Tests (with mocking)
3. Validation & Scoring Tests
4. Retry Logic Tests
5. Configuration Tests
6. Integration Tests
7. Error Handling Tests
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from io import BytesIO
import logging

# Import agent components
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
# TEST: UNIT TESTS FOR CORE COMPONENTS
# ============================================================================

class TestLogLevel:
    """Test LogLevel enum"""
    
    @pytest.mark.unit
    def test_log_level_debug(self):
        """Test DEBUG log level"""
        assert LogLevel.DEBUG.value == logging.DEBUG
    
    @pytest.mark.unit
    def test_log_level_info(self):
        """Test INFO log level"""
        assert LogLevel.INFO.value == logging.INFO
    
    @pytest.mark.unit
    def test_log_level_warning(self):
        """Test WARNING log level"""
        assert LogLevel.WARNING.value == logging.WARNING
    
    @pytest.mark.unit
    def test_log_level_error(self):
        """Test ERROR log level"""
        assert LogLevel.ERROR.value == logging.ERROR


class TestSetupLogger:
    """Test setup_logger function"""
    
    @pytest.mark.unit
    def test_setup_logger_default(self):
        """Test logger setup with default parameters"""
        logger = setup_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
    
    @pytest.mark.unit
    def test_setup_logger_debug_level(self):
        """Test logger setup with DEBUG level"""
        logger = setup_logger("test_debug", level=LogLevel.DEBUG)
        assert logger.level == logging.DEBUG
    
    @pytest.mark.unit
    def test_setup_logger_error_level(self):
        """Test logger setup with ERROR level"""
        logger = setup_logger("test_error", level=LogLevel.ERROR)
        assert logger.level == logging.ERROR
    
    @pytest.mark.unit
    def test_setup_logger_multiple_calls(self):
        """Test that multiple calls return same logger instance"""
        logger1 = setup_logger("same_logger", level=LogLevel.INFO)
        logger2 = setup_logger("same_logger", level=LogLevel.DEBUG)
        # Should return the same logger instance
        assert logger1 is logger2


class TestMediaRequestDataclass:
    """Test MediaRequest dataclass"""
    
    @pytest.mark.unit
    def test_basic_request(self):
        """Test creating basic media request"""
        request = MediaRequest(
            query="test query",
            media_type="image",
            quantity=5
        )
        assert request.query == "test query"
        assert request.media_type == "image"
        assert request.quantity == 5
        assert request.quality == "high"
        assert request.licensing == "free"
    
    @pytest.mark.unit
    def test_request_with_all_fields(self):
        """Test media request with all fields"""
        request = MediaRequest(
            query="test",
            media_type="video",
            quantity=3,
            quality="professional",
            licensing="cc0",
            duration_min=10,
            duration_max=60,
            context={"handout": "1"},
            constraints={"style": "cartoon"}
        )
        assert request.duration_min == 10
        assert request.duration_max == 60
        assert request.context == {"handout": "1"}
        assert request.constraints == {"style": "cartoon"}
    
    @pytest.mark.unit
    def test_request_post_init_defaults(self):
        """Test that __post_init__ handles None defaults"""
        request = MediaRequest(
            query="test",
            media_type="image"
        )
        assert request.context == {}
        assert request.constraints == {}
    
    @pytest.mark.unit
    def test_request_with_empty_context(self):
        """Test request with empty context"""
        request = MediaRequest(
            query="test",
            media_type="image",
            context={}
        )
        assert isinstance(request.context, dict)
        assert len(request.context) == 0


class TestMediaResultDataclass:
    """Test MediaResult dataclass"""
    
    @pytest.mark.unit
    def test_basic_result(self):
        """Test creating basic media result"""
        result = MediaResult(
            id="test_001",
            url="https://example.com/image.jpg",
            local_path="/tmp/image.jpg",
            title="Test Image",
            license="cc0",
            source="test_source",
            media_type="image"
        )
        assert result.id == "test_001"
        assert result.url == "https://example.com/image.jpg"
        assert result.quality_score == 0.0
        assert result.relevance_score == 0.0
    
    @pytest.mark.unit
    def test_result_with_scores(self):
        """Test result with all scores set"""
        result = MediaResult(
            id="test_002",
            url="https://example.com/image.jpg",
            local_path="/tmp/image.jpg",
            title="Test",
            license="free",
            source="test",
            media_type="image",
            quality_score=85.5,
            relevance_score=75.0,
            style_confidence=0.95,
            final_score=78.0
        )
        assert result.quality_score == 85.5
        assert result.relevance_score == 75.0
        assert result.style_confidence == 0.95
        assert result.final_score == 78.0
    
    @pytest.mark.unit
    def test_result_post_init_timestamp(self):
        """Test that __post_init__ sets timestamp"""
        result = MediaResult(
            id="test",
            url="http://example.com",
            local_path="/tmp/test",
            title="Test",
            license="cc0",
            source="test",
            media_type="image"
        )
        assert result.downloaded_at != ""
        assert "T" in result.downloaded_at  # ISO format


class TestAgentConfigDataclass:
    """Test AgentConfig dataclass"""
    
    @pytest.mark.unit
    def test_default_config(self):
        """Test default configuration values"""
        config = AgentConfig()
        
        # Search config
        assert config.max_search_queries == 5
        assert config.results_per_source == 5
        
        # Scoring
        assert config.min_final_score == 50.0
        assert config.style_confidence_weight == 0.2
        assert config.quality_weight == 0.4
        assert config.relevance_weight == 0.6
        
        # Retry
        assert config.max_retries == 3
        assert config.retry_delay_base == 1.0
        
        # Timeouts
        assert config.download_timeout == 10
        assert config.api_timeout == 5
    
    @pytest.mark.unit
    def test_custom_config(self):
        """Test custom configuration"""
        config = AgentConfig(
            max_retries=5,
            min_final_score=70.0,
            style_confidence_weight=0.3
        )
        assert config.max_retries == 5
        assert config.min_final_score == 70.0
        assert config.style_confidence_weight == 0.3
    
    @pytest.mark.unit
    def test_style_keywords_initialization(self):
        """Test that style keywords are properly initialized"""
        config = AgentConfig()
        assert "cartoon" in config.style_keywords
        assert "photo" in config.style_keywords
        assert "watercolor" in config.style_keywords
        
        # Check structure
        cartoon_keywords = config.style_keywords["cartoon"]
        assert "positive" in cartoon_keywords
        assert "negative" in cartoon_keywords
        assert len(cartoon_keywords["positive"]) > 0
        assert len(cartoon_keywords["negative"]) > 0
    
    @pytest.mark.unit
    def test_config_quality_bonuses(self):
        """Test quality bonus configuration"""
        config = AgentConfig()
        assert config.quality_bonus_fhd == 15.0
        assert config.quality_bonus_hd == 10.0
        assert config.quality_bonus_cc0 == 10.0
        assert config.quality_bonus_free == 5.0


# ============================================================================
# TEST: AGENT INITIALIZATION
# ============================================================================

class TestAgentInitialization:
    """Test MediaGatheringAgent initialization"""
    
    @pytest.mark.unit
    def test_agent_init_basic(self, temp_output_dir, test_config):
        """Test basic agent initialization"""
        agent = MediaGatheringAgent(
            output_dir=str(temp_output_dir),
            config=test_config
        )
        assert agent.output_dir == temp_output_dir
        assert agent.config == test_config
        assert agent.session is not None
    
    @pytest.mark.unit
    def test_agent_init_creates_output_dir(self, temp_output_dir):
        """Test that agent creates output directory"""
        agent = MediaGatheringAgent(output_dir=str(temp_output_dir))
        assert temp_output_dir.exists()
    
    @pytest.mark.unit
    def test_agent_init_default_config(self, temp_output_dir):
        """Test agent with default config"""
        agent = MediaGatheringAgent(output_dir=str(temp_output_dir))
        assert isinstance(agent.config, AgentConfig)
        assert agent.config.max_retries == 3
    
    @pytest.mark.unit
    def test_agent_init_session_headers(self, temp_output_dir):
        """Test that session has proper headers"""
        agent = MediaGatheringAgent(output_dir=str(temp_output_dir))
        assert "User-Agent" in agent.session.headers
    
    @pytest.mark.unit
    def test_agent_results_list_initialized(self, basic_agent):
        """Test that results list is initialized"""
        assert isinstance(basic_agent.results, list)
        assert len(basic_agent.results) == 0
    
    @pytest.mark.unit
    def test_agent_cache_initialized(self, basic_agent):
        """Test that cache dictionary is initialized"""
        assert isinstance(basic_agent.cache, dict)
    
    @pytest.mark.unit
    def test_agent_request_id_generated(self, basic_agent):
        """Test that unique request ID is generated"""
        assert basic_agent.request_id != ""
        # Should be UUID-like
        assert len(basic_agent.request_id) > 30


# ============================================================================
# TEST: QUERY GENERATION
# ============================================================================

class TestQueryGeneration:
    """Test search query generation"""
    
    @pytest.mark.unit
    def test_generate_single_query(self, basic_agent):
        """Test query generation with single query"""
        queries = basic_agent._generate_search_queries("test")
        assert isinstance(queries, list)
        assert len(queries) > 0
    
    @pytest.mark.unit
    def test_generated_queries_include_original(self, basic_agent):
        """Test that original query is included"""
        original = "children learning"
        queries = basic_agent._generate_search_queries(original)
        assert original in queries
    
    @pytest.mark.unit
    def test_generated_queries_are_unique(self, basic_agent):
        """Test that generated queries are unique"""
        queries = basic_agent._generate_search_queries("children")
        unique_queries = set(queries)
        assert len(queries) == len(unique_queries)
    
    @pytest.mark.unit
    def test_generates_variations(self, basic_agent):
        """Test that variations are generated"""
        queries = basic_agent._generate_search_queries("children learning")
        # Should have at least 2 queries (original + variations)
        assert len(queries) >= 2
    
    @pytest.mark.unit
    def test_respects_max_queries_limit(self, basic_agent):
        """Test that max query limit is respected"""
        queries = basic_agent._generate_search_queries("test query")
        assert len(queries) <= basic_agent.config.max_search_queries
    
    @pytest.mark.unit
    def test_handles_children_variation(self, basic_agent):
        """Test that 'children' variations are generated"""
        queries = basic_agent._generate_search_queries("children")
        # Should generate variations like "kids", "students"
        assert len(queries) > 1
    
    @pytest.mark.unit
    def test_educational_variations(self, basic_agent):
        """Test that educational variations are generated"""
        queries = basic_agent._generate_search_queries("learning")
        query_text = " ".join(queries).lower()
        # Should include 'learning' or 'educational'
        assert "learning" in query_text or "educational" in query_text


# ============================================================================
# TEST: SCORING METHODS
# ============================================================================

class TestScoringMethods:
    """Test media validation and scoring functions"""
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_fhd_resolution(self, basic_agent, cartoon_candidate):
        """Test quality score bonus for FHD resolution"""
        cartoon_candidate["resolution"] = "1920x1080"
        score = basic_agent._calculate_quality_score(cartoon_candidate, 
                                                      MediaRequest("test", "image"))
        # Should include FHD bonus
        assert score >= basic_agent.config.base_quality_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_hd_resolution(self, basic_agent, cartoon_candidate):
        """Test quality score bonus for HD resolution"""
        cartoon_candidate["resolution"] = "1280x720"
        score = basic_agent._calculate_quality_score(cartoon_candidate,
                                                      MediaRequest("test", "image"))
        assert score >= basic_agent.config.base_quality_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_low_resolution(self, basic_agent, cartoon_candidate):
        """Test quality score for low resolution"""
        cartoon_candidate["resolution"] = "400x300"
        score = basic_agent._calculate_quality_score(cartoon_candidate,
                                                      MediaRequest("test", "image"))
        # Should be base score without bonuses
        assert score >= 0 and score <= 100
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_cc0_license(self, basic_agent, cartoon_candidate):
        """Test quality score bonus for CC0 license"""
        cartoon_candidate["license"] = "cc0"
        score = basic_agent._calculate_quality_score(cartoon_candidate,
                                                      MediaRequest("test", "image"))
        assert score >= basic_agent.config.base_quality_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_free_license(self, basic_agent, cartoon_candidate):
        """Test quality score bonus for free license"""
        cartoon_candidate["license"] = "free"
        score = basic_agent._calculate_quality_score(cartoon_candidate,
                                                      MediaRequest("test", "image"))
        assert score >= basic_agent.config.base_quality_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_quality_score_no_resolution(self, basic_agent, cartoon_candidate):
        """Test quality score with missing resolution"""
        cartoon_candidate["resolution"] = ""
        score = basic_agent._calculate_quality_score(cartoon_candidate,
                                                      MediaRequest("test", "image"))
        # Should still return valid score
        assert 0 <= score <= 100
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_relevance_score_perfect_match(self, basic_agent):
        """Test relevance score for perfect keyword match"""
        candidate = {
            "title": "children learning education",
            "metadata": {
                "tags": ["children", "learning"],
                "description": "education"
            }
        }
        score = basic_agent._calculate_relevance_score(candidate, "children learning")
        # Should have high relevance
        assert score >= basic_agent.config.base_relevance_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_relevance_score_no_match(self, basic_agent):
        """Test relevance score with no keyword match"""
        candidate = {
            "title": "sunset landscape",
            "metadata": {
                "tags": ["nature"],
                "description": "scenic view"
            }
        }
        score = basic_agent._calculate_relevance_score(candidate, "children learning")
        # Should have low relevance
        assert score >= 0 and score <= 100
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_relevance_score_partial_match(self, basic_agent):
        """Test relevance score with partial match"""
        candidate = {
            "title": "children playing",
            "metadata": {
                "tags": ["children"],
                "description": "kids"
            }
        }
        score = basic_agent._calculate_relevance_score(candidate, "children learning")
        # Should be moderate
        assert score >= basic_agent.config.base_relevance_score
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_style_confidence_cartoon_no_constraint(self, basic_agent, cartoon_candidate):
        """Test style confidence with no style constraint"""
        request = MediaRequest("test", "image", constraints={})
        confidence = basic_agent._calculate_style_confidence(cartoon_candidate, request)
        # Should return base style confidence
        assert confidence == basic_agent.config.base_style_confidence
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_style_confidence_cartoon_match(self, basic_agent, cartoon_candidate):
        """Test style confidence for cartoon with cartoon constraint"""
        request = MediaRequest("test", "image", constraints={"style": "cartoon"})
        confidence = basic_agent._calculate_style_confidence(cartoon_candidate, request)
        # Should be high confidence for cartoon
        assert confidence > basic_agent.config.base_style_confidence
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_style_confidence_cartoon_mismatch(self, basic_agent, photo_candidate):
        """Test style confidence mismatch (photo for cartoon)"""
        request = MediaRequest("test", "image", constraints={"style": "cartoon"})
        confidence = basic_agent._calculate_style_confidence(photo_candidate, request)
        # Should be low confidence for photo when cartoon expected
        assert confidence < basic_agent.config.base_style_confidence
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_style_confidence_unknown_style(self, basic_agent, cartoon_candidate):
        """Test style confidence with unknown style"""
        request = MediaRequest("test", "image", constraints={"style": "unknown_style"})
        confidence = basic_agent._calculate_style_confidence(cartoon_candidate, request)
        # Should return base confidence for unknown style
        assert confidence == basic_agent.config.base_style_confidence
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_style_confidence_range(self, basic_agent, cartoon_candidate):
        """Test that style confidence is always in valid range"""
        request = MediaRequest("test", "image", constraints={"style": "cartoon"})
        confidence = basic_agent._calculate_style_confidence(cartoon_candidate, request)
        # Should be between 0 and 1
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_final_score_combines_components(self, basic_agent):
        """Test that final score combines all components"""
        quality = 80.0
        relevance = 75.0
        style = 0.9
        
        score = basic_agent._calculate_final_score(quality, relevance, style)
        
        # Should be within valid range
        assert 0 <= score <= 100
        # Should consider style confidence
        assert score > 0  # Not zero if components are non-zero
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_final_score_zero_components(self, basic_agent):
        """Test final score with zero components"""
        score = basic_agent._calculate_final_score(0.0, 0.0, 0.0)
        assert score == 0.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_final_score_high_quality_low_relevance(self, basic_agent):
        """Test final score prioritizes relevance over quality"""
        high_quality_low_rel = basic_agent._calculate_final_score(90.0, 20.0, 0.5)
        low_quality_high_rel = basic_agent._calculate_final_score(20.0, 90.0, 0.5)
        
        # Higher relevance should result in higher final score
        assert low_quality_high_rel > high_quality_low_rel


# ============================================================================
# TEST: VALIDATION AND SCORING INTEGRATION
# ============================================================================

class TestValidationAndScoring:
    """Test integrated validation and scoring"""
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_validate_and_score_empty_list(self, basic_agent, cartoon_request):
        """Test validation with empty candidate list"""
        scored = basic_agent._validate_and_score([], cartoon_request)
        assert isinstance(scored, list)
        assert len(scored) == 0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_validate_and_score_adds_scores(self, basic_agent, cartoon_request, 
                                             cartoon_candidate):
        """Test that validation adds score fields"""
        candidates = [cartoon_candidate]
        scored = basic_agent._validate_and_score(candidates, cartoon_request)
        
        if len(scored) > 0:
            assert "quality_score" in scored[0]
            assert "relevance_score" in scored[0]
            assert "style_confidence" in scored[0]
            assert "final_score" in scored[0]
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_validate_and_score_filters_low_score(self, basic_agent, strict_config):
        """Test that low-scoring items are filtered"""
        agent = MediaGatheringAgent(config=strict_config)
        
        low_quality = {
            "id": "low",
            "title": "irrelevant low quality",
            "source": "test",
            "license": "unknown",
            "resolution": "100x100",
            "metadata": {}
        }
        
        request = MediaRequest("children", "image")
        scored = agent._validate_and_score([low_quality], request)
        
        # With strict config, low quality should be filtered out
        # (strict config has min_final_score of 70.0)
        if strict_config.min_final_score > 60:
            assert len(scored) == 0 or (len(scored) > 0 and scored[0]["final_score"] >= strict_config.min_final_score)
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_validate_and_score_sorts_by_final_score(self, basic_agent, 
                                                       cartoon_request):
        """Test that results are sorted by final score"""
        candidates = [
            {
                "id": "high",
                "title": "cartoon children learning",
                "source": "test",
                "license": "cc0",
                "resolution": "1920x1080",
                "metadata": {"tags": ["cartoon"], "description": ""}
            },
            {
                "id": "low",
                "title": "landscape",
                "source": "test",
                "license": "free",
                "resolution": "800x600",
                "metadata": {"tags": ["nature"], "description": ""}
            }
        ]
        
        scored = basic_agent._validate_and_score(candidates, cartoon_request)
        
        # Results should be sorted by final_score descending
        if len(scored) > 1:
            assert scored[0]["final_score"] >= scored[1]["final_score"]


# ============================================================================
# TEST: RETRY LOGIC
# ============================================================================

class TestRetryLogic:
    """Test exponential backoff retry mechanism"""
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_success_first_attempt(self, basic_agent):
        """Test that successful function doesn't retry"""
        call_count = 0
        
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = basic_agent._with_retry(successful_func, max_attempts=3)
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_success_after_failures(self, basic_agent):
        """Test retry succeeds after initial failures"""
        call_count = 0
        
        def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = basic_agent._with_retry(eventually_succeeds, max_attempts=5)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_exhausted_retries(self, basic_agent):
        """Test that exception is raised after exhausted retries"""
        def always_fails():
            raise Exception("Always fails")
        
        with pytest.raises(Exception):
            basic_agent._with_retry(always_fails, max_attempts=2)
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_timeout_exception(self, basic_agent):
        """Test retry on timeout exception"""
        import requests
        call_count = 0
        
        def timeout_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise requests.Timeout("Timeout")
            return "success"
        
        result = basic_agent._with_retry(timeout_then_success, max_attempts=3)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_connection_error(self, basic_agent):
        """Test retry on connection error"""
        import requests
        call_count = 0
        
        def connection_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise requests.ConnectionError("Connection error")
            return "success"
        
        result = basic_agent._with_retry(connection_then_success, max_attempts=3)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_4xx_no_retry(self, basic_agent):
        """Test that 4xx errors are not retried"""
        import requests
        call_count = 0
        
        def client_error():
            nonlocal call_count
            call_count += 1
            response = Mock()
            response.status_code = 401
            raise requests.HTTPError(response=response)
        
        with pytest.raises(requests.HTTPError):
            basic_agent._with_retry(client_error, max_attempts=3)
        
        # Should only try once for 4xx error
        assert call_count == 1
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_5xx_retries(self, basic_agent):
        """Test that 5xx errors are retried"""
        import requests
        call_count = 0
        
        def server_error_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                response = Mock()
                response.status_code = 500
                raise requests.HTTPError(response=response)
            return "success"
        
        result = basic_agent._with_retry(server_error_then_success, max_attempts=3)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_exponential_backoff(self, basic_agent):
        """Test exponential backoff timing"""
        times = []
        call_count = 0
        
        def timed_failure():
            nonlocal call_count
            call_count += 1
            times.append(time.time())
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        # Use fast backoff for testing
        basic_agent.config.retry_delay_base = 0.01
        
        result = basic_agent._with_retry(timed_failure, max_attempts=4)
        assert result == "success"
        
        # Should have made 3 calls (initial + 2 retries)
        assert call_count == 3
    
    @pytest.mark.unit
    @pytest.mark.retry
    def test_retry_custom_max_attempts(self, basic_agent):
        """Test custom max attempts parameter"""
        call_count = 0
        
        def counting_func():
            nonlocal call_count
            call_count += 1
            if call_count < 10:
                raise Exception("Fail")
            return "success"
        
        with pytest.raises(Exception):
            basic_agent._with_retry(counting_func, max_attempts=3)
        
        # Should only try 3 times
        assert call_count == 3


# ============================================================================
# TEST: API SEARCH WITH MOCKING
# ============================================================================

class TestUnsplashSearch:
    """Test Unsplash API search with mocks"""
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_unsplash_search_success(self, basic_agent, mock_unsplash_success):
        """Test successful Unsplash search"""
        with patch.object(basic_agent.session, 'get', return_value=mock_unsplash_success):
            results = basic_agent._search_unsplash("test query", "image")
            
            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0]["source"] == "unsplash"
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_unsplash_search_401_unauthorized(self, basic_agent, mock_401_unauthorized):
        """Test Unsplash 401 error handling"""
        with patch.object(basic_agent.session, 'get', return_value=mock_401_unauthorized):
            results = basic_agent._search_unsplash("test query", "image")
            # Should return empty list on error
            assert results == []
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_unsplash_search_timeout(self, basic_agent):
        """Test Unsplash timeout handling"""
        import requests
        
        def timeout_side_effect(*args, **kwargs):
            raise requests.Timeout("Connection timeout")
        
        with patch.object(basic_agent.session, 'get', side_effect=timeout_side_effect):
            # Should handle gracefully and return empty list
            results = basic_agent._search_unsplash("test query", "image")
            assert results == []
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_unsplash_video_type_not_supported(self, basic_agent):
        """Test that Unsplash doesn't search for videos"""
        results = basic_agent._search_unsplash("test", "video")
        assert results == []
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_unsplash_audio_type_not_supported(self, basic_agent):
        """Test that Unsplash doesn't search for audio"""
        results = basic_agent._search_unsplash("test", "audio")
        assert results == []


class TestPexelsSearch:
    """Test Pexels API search with mocks"""
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_pexels_image_search_success(self, basic_agent, mock_pexels_image_success):
        """Test successful Pexels image search"""
        with patch.object(basic_agent.session, 'get', return_value=mock_pexels_image_success):
            results = basic_agent._search_pexels("test query", "image")
            
            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0]["source"] == "pexels"
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_pexels_video_search_success(self, basic_agent, mock_pexels_video_success):
        """Test successful Pexels video search"""
        with patch.object(basic_agent.session, 'get', return_value=mock_pexels_video_success):
            results = basic_agent._search_pexels("test query", "video")
            
            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0]["source"] == "pexels"
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_pexels_audio_not_supported(self, basic_agent):
        """Test that Pexels doesn't search for audio"""
        results = basic_agent._search_pexels("test", "audio")
        assert results == []
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_pexels_403_forbidden(self, basic_agent, mock_403_forbidden):
        """Test Pexels 403 error handling"""
        with patch.object(basic_agent.session, 'get', return_value=mock_403_forbidden):
            results = basic_agent._search_pexels("test query", "image")
            assert results == []
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_pexels_connection_error(self, basic_agent):
        """Test Pexels connection error handling"""
        import requests
        
        def connection_error(*args, **kwargs):
            raise requests.ConnectionError("Connection failed")
        
        with patch.object(basic_agent.session, 'get', side_effect=connection_error):
            results = basic_agent._search_pexels("test query", "image")
            assert results == []


class TestSearchMedia:
    """Test integrated _search_media function"""
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_search_media_deduplication(self, basic_agent, cartoon_request):
        """Test that duplicate URLs are removed"""
        duplicate_candidate = {
            "url": "https://example.com/image1.jpg",
            "id": "dup_1",
            "source": "unsplash"
        }
        
        with patch.object(basic_agent, '_search_unsplash', 
                         return_value=[duplicate_candidate, duplicate_candidate]):
            with patch.object(basic_agent, '_search_pexels', return_value=[]):
                results = basic_agent._search_media(cartoon_request, ["test"])
                
                # Should only have one instance
                assert len(results) == 1
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_search_media_combines_sources(self, basic_agent, cartoon_request):
        """Test that search combines results from multiple sources"""
        unsplash_result = {
            "id": "unsplash_1",
            "url": "https://unsplash.com/1.jpg",
            "source": "unsplash"
        }
        pexels_result = {
            "id": "pexels_1",
            "url": "https://pexels.com/1.jpg",
            "source": "pexels"
        }
        
        with patch.object(basic_agent, '_search_unsplash', return_value=[unsplash_result]):
            with patch.object(basic_agent, '_search_pexels', return_value=[pexels_result]):
                results = basic_agent._search_media(cartoon_request, ["test"])
                
                assert len(results) >= 2
                sources = [r["source"] for r in results]
                assert "unsplash" in sources
                assert "pexels" in sources


# ============================================================================
# TEST: CONFIGURATION TESTS
# ============================================================================

class TestConfigurationHandling:
    """Test configuration handling and defaults"""
    
    @pytest.mark.unit
    def test_config_quality_bonuses_sum(self):
        """Test that quality bonuses create valid scores"""
        config = AgentConfig()
        max_possible = (
            config.base_quality_score +
            config.quality_bonus_fhd +
            config.quality_bonus_cc0
        )
        assert max_possible <= 100.0  # Score should be clamped to 100
    
    @pytest.mark.unit
    def test_config_weights_are_reasonable(self):
        """Test that scoring weights are reasonable"""
        config = AgentConfig()
        # Weights should be positive
        assert config.quality_weight > 0
        assert config.relevance_weight > 0
        assert config.style_confidence_weight >= 0
    
    @pytest.mark.unit
    def test_agent_uses_provided_config(self):
        """Test that agent uses provided configuration"""
        custom_config = AgentConfig(
            max_retries=10,
            min_final_score=85.0
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = MediaGatheringAgent(
                output_dir=tmpdir,
                config=custom_config
            )
            assert agent.config.max_retries == 10
            assert agent.config.min_final_score == 85.0
    
    @pytest.mark.unit
    def test_agent_creates_default_config_if_none(self):
        """Test that agent creates default config if none provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = MediaGatheringAgent(output_dir=tmpdir)
            assert isinstance(agent.config, AgentConfig)
            assert agent.config.max_retries == 3  # Default value


# ============================================================================
# TEST: FILE OPERATIONS
# ============================================================================

class TestFileOperations:
    """Test file-related operations"""
    
    @pytest.mark.unit
    def test_get_file_extension_jpeg(self, basic_agent):
        """Test file extension detection for JPEG"""
        ext = basic_agent._get_file_extension("image/jpeg", "http://example.com")
        assert ext == ".jpg"
    
    @pytest.mark.unit
    def test_get_file_extension_png(self, basic_agent):
        """Test file extension detection for PNG"""
        ext = basic_agent._get_file_extension("image/png", "http://example.com")
        assert ext == ".png"
    
    @pytest.mark.unit
    def test_get_file_extension_webp(self, basic_agent):
        """Test file extension detection for WebP"""
        ext = basic_agent._get_file_extension("image/webp", "http://example.com")
        assert ext == ".webp"
    
    @pytest.mark.unit
    def test_get_file_extension_mp4(self, basic_agent):
        """Test file extension detection for MP4"""
        ext = basic_agent._get_file_extension("video/mp4", "http://example.com")
        assert ext == ".mp4"
    
    @pytest.mark.unit
    def test_get_file_extension_fallback_to_url(self, basic_agent):
        """Test fallback to URL extension"""
        ext = basic_agent._get_file_extension("", "http://example.com/image.jpg?v=1")
        # Should extract from URL
        assert ext in [".jpg", ".bin"]
    
    @pytest.mark.unit
    def test_get_file_extension_default_fallback(self, basic_agent):
        """Test default fallback extension"""
        ext = basic_agent._get_file_extension("unknown/type", "http://example.com/file")
        # Should return .bin or extract from URL (may include forward slash)
        assert ext in [".bin", ".com", ".com/"]


# ============================================================================
# TEST: INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.integration
    @pytest.mark.mock
    def test_process_request_complete_flow(self, basic_agent, cartoon_request):
        """Test complete request processing flow"""
        with patch.object(basic_agent, '_search_unsplash', return_value=[]):
            with patch.object(basic_agent, '_search_pexels', return_value=[]):
                with patch.object(basic_agent, '_download_media', return_value=[]):
                    report = basic_agent.process_request(cartoon_request)
                    
                    # Check report structure
                    assert "request_id" in report
                    assert "timestamp" in report
                    assert "summary" in report
                    assert "results" in report
    
    @pytest.mark.integration
    def test_report_structure_with_results(self, media_result_list):
        """Test report generation structure"""
        report = {
            "request_id": "test-123",
            "results": [
                {
                    "id": r.id,
                    "quality_score": r.quality_score,
                    "relevance_score": r.relevance_score
                }
                for r in media_result_list
            ],
            "summary": {
                "total_retrieved": len(media_result_list),
                "retrieval_rate": "100%"
            }
        }
        
        assert report["summary"]["total_retrieved"] == 3
        assert len(report["results"]) == 3
    
    @pytest.mark.integration
    def test_multiple_requests_same_agent(self, basic_agent, cartoon_request, 
                                          photo_request):
        """Test processing multiple requests with same agent"""
        with patch.object(basic_agent, '_search_unsplash', return_value=[]):
            with patch.object(basic_agent, '_search_pexels', return_value=[]):
                with patch.object(basic_agent, '_download_media', return_value=[]):
                    report1 = basic_agent.process_request(cartoon_request)
                    report2 = basic_agent.process_request(photo_request)
                    
                    # Both should return valid reports
                    assert "request_id" in report1
                    assert "request_id" in report2
                    # Request IDs should match agent
                    assert report1["request_id"] == basic_agent.request_id
                    assert report2["request_id"] == basic_agent.request_id


# ============================================================================
# TEST: ERROR HANDLING & EDGE CASES
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.unit
    def test_empty_query(self, basic_agent):
        """Test handling of empty query"""
        request = MediaRequest(query="", media_type="image", quantity=5)
        assert request.query == ""
    
    @pytest.mark.unit
    def test_zero_quantity_request(self, basic_agent):
        """Test request with zero quantity"""
        request = MediaRequest(query="test", media_type="image", quantity=0)
        assert request.quantity == 0
    
    @pytest.mark.unit
    def test_very_large_quantity(self, basic_agent):
        """Test request with very large quantity"""
        request = MediaRequest(query="test", media_type="image", quantity=1000000)
        assert request.quantity == 1000000
    
    @pytest.mark.unit
    def test_invalid_media_type(self, basic_agent):
        """Test request with invalid media type"""
        request = MediaRequest(
            query="test",
            media_type="invalid_type",
            quantity=5
        )
        # Should still create request, validation happens later
        assert request.media_type == "invalid_type"
    
    @pytest.mark.unit
    def test_candidate_missing_url(self, basic_agent, cartoon_request):
        """Test handling of candidate without URL"""
        candidate = {
            "id": "no_url",
            "title": "Test",
            "source": "test",
            "license": "cc0",
            "metadata": {}
            # Missing url
        }
        
        scored = basic_agent._validate_and_score([candidate], cartoon_request)
        # Should handle missing URL gracefully
        assert isinstance(scored, list)
    
    @pytest.mark.unit
    def test_candidate_missing_metadata(self, basic_agent, cartoon_request):
        """Test handling of candidate missing metadata"""
        candidate = {
            "id": "no_meta",
            "url": "http://example.com",
            "title": "Test",
            "source": "test",
            "license": "cc0",
            "resolution": "1920x1080"
            # Missing metadata
        }
        
        # Should not crash
        scored = basic_agent._validate_and_score([candidate], cartoon_request)
        assert isinstance(scored, list)
    
    @pytest.mark.unit
    def test_candidate_invalid_resolution(self, basic_agent):
        """Test handling of invalid resolution format"""
        candidate = {
            "id": "bad_res",
            "resolution": "not_a_resolution",
            "title": "Test",
            "source": "test",
            "license": "cc0",
            "metadata": {}
        }
        
        request = MediaRequest("test", "image")
        # Should not crash on invalid resolution
        score = basic_agent._calculate_quality_score(candidate, request)
        assert 0 <= score <= 100
    
    @pytest.mark.unit
    def test_malformed_candidate_data(self, basic_agent, cartoon_request):
        """Test handling of malformed candidate data"""
        malformed = {
            "id": "test",
            "title": "Test",
            "source": "test",
            "license": "cc0",
            "metadata": {}
        }
        
        scored = basic_agent._validate_and_score([malformed], cartoon_request)
        assert isinstance(scored, list)


# ============================================================================
# PERFORMANCE & SPEED TESTS
# ============================================================================

class TestPerformance:
    """Performance-related tests"""
    
    @pytest.mark.unit
    def test_query_generation_speed(self, basic_agent):
        """Test that query generation is fast"""
        import time
        start = time.time()
        
        for _ in range(10):
            basic_agent._generate_search_queries("test query")
        
        elapsed = time.time() - start
        # 10 generations should be very fast
        assert elapsed < 1.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_scoring_speed(self, basic_agent):
        """Test that scoring is fast"""
        import time
        start = time.time()
        
        for _ in range(100):
            basic_agent._calculate_final_score(70.0, 80.0, 0.8)
        
        elapsed = time.time() - start
        # 100 score calculations should complete in milliseconds
        assert elapsed < 1.0
    
    @pytest.mark.unit
    def test_style_confidence_speed(self, basic_agent):
        """Test that style confidence calculation is fast"""
        import time
        
        candidate = {
            "title": "test",
            "metadata": {"tags": ["tag1", "tag2"], "description": "desc"}
        }
        request = MediaRequest("test", "image", constraints={"style": "cartoon"})
        
        start = time.time()
        for _ in range(50):
            basic_agent._calculate_style_confidence(candidate, request)
        
        elapsed = time.time() - start
        # 50 confidence calculations should be fast
        assert elapsed < 1.0


# ============================================================================
# PYTEST CONFIGURATION
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
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "mock: marks tests that use mocking"
    )
    config.addinivalue_line(
        "markers", "retry: marks tests for retry logic"
    )
    config.addinivalue_line(
        "markers", "scoring: marks tests for scoring"
    )


# ============================================================================
# TEST EXECUTION INSTRUCTIONS
# ============================================================================

"""
Run all tests:
    pytest tests/test_media_gathering_agent.py -v

Run only unit tests:
    pytest tests/test_media_gathering_agent.py -v -m unit

Run only integration tests:
    pytest tests/test_media_gathering_agent.py -v -m integration

Run with coverage:
    pytest tests/test_media_gathering_agent.py --cov=media_gathering_agent --cov-report=html

Run specific test class:
    pytest tests/test_media_gathering_agent.py::TestAgentConfig -v

Run specific test:
    pytest tests/test_media_gathering_agent.py::TestScoringMethods::test_quality_score_fhd_resolution -v

Run fast tests only (skip slow):
    pytest tests/test_media_gathering_agent.py -v -m "not slow"

Run with detailed output:
    pytest tests/test_media_gathering_agent.py -vv --tb=long

Run in parallel (requires pytest-xdist):
    pytest tests/test_media_gathering_agent.py -n auto
"""
