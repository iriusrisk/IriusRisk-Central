import streamlit as st
import time
import os
from datetime import datetime
from theme import load_css, hero, card, outline_button
from migration_utils import (
    MigrationRunner, 
    get_migration_summary, 
    save_env_variables, 
    load_env_variables
)

def stream_migration_output(migration_runner):
    """Stream migration output in real-time"""
    if 'output_container' not in st.session_state:
        st.session_state.output_container = st.empty()
    if 'status_container' not in st.session_state:
        st.session_state.status_container = st.empty()
    
    # Get new output
    new_lines = migration_runner.get_output_lines()
    if new_lines:
        st.session_state.migration_output.extend(new_lines)
    
    # Update status
    is_still_running = migration_runner.is_process_running()
    
    with st.session_state.status_container.container():
        if is_still_running:
            st.info("🔄 Migration is currently running...")
        else:
            # Check final result
            success, message = migration_runner.get_process_result()
            if success is not None:
                if message not in st.session_state.migration_output:
                    st.session_state.migration_output.append(message)
                if success:
                    st.success("🎉 Migration completed successfully!")
                else:
                    st.error("❌ Migration failed!")
    
    # Update output display
    if st.session_state.migration_output:
        output_text = '\n'.join(st.session_state.migration_output[-50:])  # Show last 50 lines
        with st.session_state.output_container.container():
            st.code(output_text, language="text")
    
    return is_still_running

st.set_page_config(
    page_title="IriusRisk V1/V2 Migration Tool",
    layout="wide",
    page_icon="🔄",
)

load_css()

# Initialize migration runner and session state early
if 'migration_runner' not in st.session_state:
    st.session_state.migration_runner = MigrationRunner()
if 'migration_output' not in st.session_state:
    st.session_state.migration_output = []

# Optional top logo - will display if file exists
logo_path = "static/logo.svg"
if os.path.exists(logo_path):
    st.logo(logo_path)
elif os.path.exists("static/logo.png"):
    st.logo("static/logo.png")

# HERO
def hero_left(col):
    with col:
        st.write("Migrate your **V1 (deprecated) components** to use V2 threat patterns for enhanced security coverage.")
        
        # Check if migration can be started
        existing_token, existing_subdomain = load_env_variables()
        prerequisite_issues = st.session_state.migration_runner.check_prerequisites()
        is_running = st.session_state.migration_runner.is_process_running()
        
        can_start = existing_token and existing_subdomain and not prerequisite_issues and not is_running
        
        if can_start:
            if st.button("🚀 Start Migration", type="primary", key="hero_start"):
                success, message = st.session_state.migration_runner.start_migration(False)  # Default: not test mode
                if success:
                    st.success(message)
                    st.session_state.migration_output = [message]
                    # Clear containers for fresh start
                    if 'output_container' in st.session_state:
                        del st.session_state.output_container
                    if 'status_container' in st.session_state:
                        del st.session_state.status_container
                    st.rerun()
                else:
                    st.error(message)
        elif is_running:
            st.info("🔄 Migration is currently running...")
        elif not existing_token or not existing_subdomain:
            st.warning("⚠️ Please configure API credentials below")
        elif prerequisite_issues:
            st.error("❌ Prerequisites not met - check configuration section")
        
        outline_button("View Documentation", "https://github.com/iriusrisk/IriusRisk-Central")  # white outlined

def hero_right(col):
    with col:
        st.image("https://cdn.prod.website-files.com/650038f43bd74338d2d25f41/68d42e53fdb90004e878ee8f_IR%20Homepage%20Hero%20UPDATE%202025.svg")

hero(
    title="V1 → V2 Component Migration",
    subtitle="Automated Migration Tool for IriusRisk Components",
    left=hero_left,
    right=hero_right,
)

# BODY (centered container & cards)
st.markdown('<div class="irius-container">', unsafe_allow_html=True)
st.markdown("## Migration Process Overview")
st.write("This tool automates the migration of V1 (deprecated) components to use V2 threat patterns, ensuring your security models stay current with the latest threat intelligence.")

c1, c2, c3 = st.columns(3, gap="large")
with c1: 
    card("Phase 1", "Collect V1 (deprecated) components from your IriusRisk instance.")
with c2: 
    card("Phase 2", "Collect V2 (modern) components and their threat patterns.")
with c3: 
    card("Phase 3", "Transfer risk patterns from V2 to V1 components automatically.")

st.markdown("---")

st.markdown("## Configuration")
st.write("Before running the migration, please configure your IriusRisk API credentials:")

# Load existing values from .env
existing_token, existing_subdomain = load_env_variables()

col1, col2 = st.columns(2)

with col1:
    api_token = st.text_input(
        "API Token", 
        value=existing_token,
        type="password", 
        help="Your IriusRisk API token with appropriate permissions"
    )
    
with col2:
    subdomain = st.text_input(
        "Subdomain",
        value=existing_subdomain,
        placeholder="e.g., r2, demo", 
        help="Your IriusRisk subdomain (without .iriusrisk.com)"
    )

# Save credentials when they change
if api_token != existing_token or subdomain != existing_subdomain:
    if api_token and subdomain:
        save_env_variables(api_token, subdomain)
        st.success("✅ Credentials saved to .env file!")

# Initialize last_check_time (other session state already initialized at the top)
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = 0

# Check prerequisites
prerequisite_issues = st.session_state.migration_runner.check_prerequisites()

if api_token and subdomain:
    if not prerequisite_issues:
        st.success("✅ Configuration looks good! Ready to start migration.")
        
        # Advanced options
        with st.expander("Advanced Options"):
            test_mode = st.checkbox("Test Mode", help="Run with limited processing for faster execution")
            if test_mode:
                st.warning("⚠️ Test mode will process a limited subset of data")
        
        # Check if migration is currently running
        is_running = st.session_state.migration_runner.is_process_running()
        
        # Migration controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if not is_running:
                if st.button("🚀 Run Full Migration", type="primary"):
                    success, message = st.session_state.migration_runner.start_migration(test_mode)
                    if success:
                        st.success(message)
                        st.session_state.migration_output = [message]
                        # Clear containers for fresh start
                        if 'output_container' in st.session_state:
                            del st.session_state.output_container
                        if 'status_container' in st.session_state:
                            del st.session_state.status_container
                        st.rerun()
                    else:
                        st.error(message)
            else:
                if st.button("🛑 Stop Migration"):
                    if st.session_state.migration_runner.stop_migration():
                        st.warning("Migration stopped by user")
                        st.rerun()
        
        with col2:
            if st.button("📊 View Results Summary"):
                st.session_state.show_summary = True
        
        with col3:
            if st.button("🔄 Refresh Status"):
                st.rerun()
        
        # Handle migration streaming
        if is_running:
            st.markdown("### Migration Progress")
            
            # Stream the migration output
            is_still_running = stream_migration_output(st.session_state.migration_runner)
            
            # Auto-refresh while running
            if is_still_running:
                time.sleep(1)
                st.rerun()
        
        # Display completed migration output
        elif st.session_state.migration_output:
            st.markdown("### Migration Results")
            output_text = '\n'.join(st.session_state.migration_output)
            st.code(output_text, language="text")
        
        # Show results summary if requested
        if st.session_state.get('show_summary', False):
            st.markdown("### Migration Results Summary")
            summary = get_migration_summary()
            for item in summary:
                st.write(item)
            
            if st.button("Hide Summary"):
                st.session_state.show_summary = False
                
    else:
        st.error("❌ Prerequisites not met:")
        for issue in prerequisite_issues:
            st.write(issue)
        st.info("Please ensure all required files are present before running the migration.")
        
else:
    st.warning("⚠️ Please provide both API Token and Subdomain to proceed")

st.markdown("---")

st.markdown("## Status & Logs")

# Live migration output
with st.expander("View Live Migration Output"):
    if st.session_state.migration_output:
        st.code('\n'.join(st.session_state.migration_output), language="text")
    else:
        st.code("Live migration output will appear here when the process runs...", language="text")

# Log file content
col1, col2 = st.columns([3, 1])
with col1:
    with st.expander("View Migration Log File (migration.log)"):
        if st.button("🔄 Refresh Log"):
            pass  # Will trigger rerun and refresh
        
        log_content = st.session_state.migration_runner.get_log_content()
        st.code(log_content, language="text")

with col2:
    st.markdown("### Log Actions")
    if st.button("🗑️ Clear Log"):
        if st.session_state.migration_runner.clear_log():
            st.success("Log file cleared!")
            st.rerun()
        else:
            st.error("Failed to clear log file")
    
    if st.button("💾 Download Log"):
        try:
            log_content = st.session_state.migration_runner.get_log_content()
            st.download_button(
                label="⬇️ Download migration.log",
                data=log_content,
                file_name=f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error preparing download: {e}")
        
# Add some helpful information
st.markdown("## Help & Documentation")
with st.expander("How to use this tool"):
    st.markdown("""
    ### Prerequisites
    1. Ensure `v1_v2_component_mappings.json` exists in the current directory
    2. Verify all required Python scripts are present in the `src/` directory
    3. Configure your IriusRisk API credentials above
    
    ### Migration Process
    1. **Phase 1**: Collect V1 (deprecated) components from your IriusRisk instance
    2. **Phase 2**: Collect V2 (modern) components and their threat patterns
    3. **Phase 4a**: Extract risk patterns from V2 components
    4. **Phase 4b**: Transfer risk patterns to V1 components
    
    ### Test Mode
    Enable test mode for faster execution with limited data processing - useful for testing the setup.
    
    ### Results
    After migration completes, check the "View Results Summary" to see generated files and statistics.
    """)

st.markdown('</div>', unsafe_allow_html=True)