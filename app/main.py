"""
SWMAP Pipeline - Main Entry Point
Config-driven pipeline execution with interactive menu
"""
from app.core.logger import setup_logger
from app.pipeline.config_loader import ConfigLoader
from app.pipeline.pipeline_runner import PipelineRunner


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("  🚀 SWMAP - Web Scraping & Monitoring Pipeline")
    print("  📊 Config-Driven Pipeline System v0.7")
    print("=" * 60)


def print_menu(pipelines):
    """Print the dynamic menu based on loaded pipelines."""
    print("\n📋 Available Pipelines:")
    print("-" * 40)
    
    for i, pipeline in enumerate(pipelines, 1):
        icon = "🌐" if pipeline.type == "static" else "⚡"
        status = "✓" if pipeline.enabled else "✗"
        print(f"  [{i}] {icon} {pipeline.name} ({pipeline.type}) [{status}]")
    
    print()
    print(f"  [{len(pipelines) + 1}] 🔄 Run All Enabled Pipelines")
    print()
    print("  [0] ❌ Exit")
    print("-" * 40)


def run_pipeline(config, logger):
    """Run a single pipeline."""
    if not config.enabled:
        print(f"\n⚠️ Pipeline '{config.name}' is disabled. Skipping.")
        return []
    
    runner = PipelineRunner(config)
    items = runner.run()
    logger.info(f"Pipeline '{config.name}' completed: {len(items)} items")
    return items


def main():
    """Main entry point with dynamic config-driven menu."""
    logger = setup_logger()
    logger.info("SWMAP Pipeline started")
    
    # Load pipeline configurations
    config_loader = ConfigLoader("config/pipelines")
    pipelines = config_loader.load_all()
    
    if not pipelines:
        print("\n❌ No pipeline configurations found in config/pipelines/")
        print("   Create YAML files to define your pipelines.")
        return
    
    print_header()
    print(f"\n📂 Loaded {len(pipelines)} pipeline(s) from config/pipelines/")
    
    while True:
        print_menu(pipelines)
        
        try:
            choice = input("\n👉 Enter your choice: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        
        # Handle exit
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        # Handle "Run All"
        if choice == str(len(pipelines) + 1):
            print("\n🔄 Running all enabled pipelines...")
            enabled = config_loader.get_enabled()
            for config in enabled:
                run_pipeline(config, logger)
            print("\n✅ All pipelines complete!")
        
        # Handle individual pipeline selection
        elif choice.isdigit() and 1 <= int(choice) <= len(pipelines):
            idx = int(choice) - 1
            config = pipelines[idx]
            run_pipeline(config, logger)
        
        else:
            print("\n❌ Invalid choice. Please try again.")
            continue
        
        # Ask to continue
        try:
            again = input("\n🔁 Run another pipeline? (y/n): ").strip().lower()
            if again != 'y':
                print("\n👋 Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()
