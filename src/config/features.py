"""Feature flags and behavior toggles based on environment."""

from src.config.environment import get_config


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled in current environment."""
    config = get_config()
    features = config.features
    return features.get(feature, False)


def show_feature_badge():
    """Show environment info in UI (for debugging)."""
    import streamlit as st
    config = get_config()
    
    with st.sidebar:
        with st.expander("📊 Environment Info", expanded=False):
            st.write(f"**Environment:** `{config.environment.value}`")
            st.write(f"**API URL:** `{config.api_url[:50]}...`" if config.api_url else "❌ Not set")
            st.write(f"**Storage:** `{config.storage_backend}`")
            st.write(f"**Debug:** `{config.debug}`")
            
            # Show enabled features
            st.subheader("Features")
            for feature, enabled in config.features.items():
                status = "✅" if enabled else "❌"
                st.write(f"{status} {feature}")
