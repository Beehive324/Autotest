import pytest
from src.main.configuration import Configuration, load_configuration

def test_configuration_initialization():
    """Test that configuration can be initialized with default values."""
    config = Configuration()
    assert config is not None
    assert hasattr(config, 'tavily_api_key')
    assert hasattr(config, 'target')

def test_load_configuration():
    """Test loading configuration from environment variables."""
    config = load_configuration()
    assert isinstance(config, Configuration)

def test_configuration_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError):
        Configuration(target="")  # Empty target should raise error

def test_configuration_api_key_validation():
    """Test API key validation."""
    with pytest.raises(ValueError):
        Configuration(tavily_api_key="")  # Empty API key should raise error

def test_configuration_target_format():
    """Test target format validation."""
    # Valid target
    config = Configuration(target="example.com")
    assert config.target == "example.com"
    
    # Invalid target
    with pytest.raises(ValueError):
        Configuration(target="not a valid domain")
