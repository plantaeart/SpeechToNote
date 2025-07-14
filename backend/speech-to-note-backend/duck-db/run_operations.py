import logging
from connection import DuckDBMongoDB
from operations_speaker_notes import DatabaseSpeakerNotesOperations
from config import DEFAULT_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OperationsTester:
    def __init__(self):
        self.db_connection = None
        self.db_operations = None
        
    # Connect to MongoDB and DuckDB
    # This method initializes the DuckDBMongoDB connection and sets up operations
    def connect_to_database(self):
        """Initialize database connections"""
        try:
            print("🔄 Connecting to MongoDB and DuckDB...")
            self.db_connection = DuckDBMongoDB(
                mongo_uri=DEFAULT_CONFIG['mongo_uri'],
                db_name=DEFAULT_CONFIG['db_name']
            )
            self.db_connection.connect()
            self.db_operations = DatabaseSpeakerNotesOperations(self.db_connection)
            print("✅ Successfully connected to MongoDB and DuckDB")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    # Search notes by keyword
    # This method allows users to search speaker notes by a keyword
    def search_notes(self):
        """Test search functionality"""
        search_term = input("Enter search term: ")
        limit = input("Enter limit (default 10): ") or "10"
        
        try:
            if not self.db_operations:
                raise Exception("Database operations not initialized. Call connect_to_database() first.")

            results = self.db_operations.search_speaker_notes(search_term, limit=int(limit))
            print(f"\n📝 Found {len(results)} results:")
            for i, note in enumerate(results[:5], 1):  # Show first 5
                print(f"{i}. Id_note: {note.get('id_note', 'N/A')}")
                print(f"   Title: {note.get('title', 'No title')}")
                print(f"   Content: {str(note.get('content', 'No content'))[:100]}...")
                print(f"   Created: {note.get('created_at', 'N/A')}")
                print("-" * 50)
        except Exception as e:
            print(f"❌ Search failed: {e}")
    
    # Get notes by date range
    # This method retrieves speaker notes created within a specific date range
    def get_date_range_notes(self):
        """Test date range functionality"""
        if not self.db_operations:
            print("❌ Database operations not initialized. Please connect first.")
            return

        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        
        try:
            results = self.db_operations.get_speaker_notes_by_date_range(start_date, end_date)
            print(f"\n📅 Found {len(results)} notes in date range:")
            for i, note in enumerate(results[:3], 1):  # Show first 3
                print(f"{i}. {note.get('title', 'No title')} - {note.get('created_at', 'N/A')}")
        except Exception as e:
            print(f"❌ Date range query failed: {e}")
    
    # Get analytics for speaker notes
    # This method retrieves various analytics about speaker notes
    def get_analytics(self):
        """Test analytics functionality"""
        if not self.db_operations:
            print("❌ Database operations not initialized. Please connect first.")
            return

        days = input("Enter number of days for analytics (default 30): ") or "30"
        
        try:
            analytics = self.db_operations.get_speaker_notes_analytics(days=int(days))
            print(f"\n📊 Analytics for last {days} days:")
            print(f"Total Notes: {analytics.get('total_speaker_notes', 0)}")
            print(f"Average Content Length: {analytics.get('avg_content_length', 0):.2f}")
            
            print("\n📈 Notes by Date:")
            for date_info in analytics.get('speaker_notes_by_date', [])[:5]:
                print(f"  {date_info.get('date')}: {date_info.get('count')} notes")
            
            print("\n⏰ Most Active Hours:")
            for hour_info in analytics.get('most_active_hours', []):
                print(f"  Hour {hour_info.get('hour')}: {hour_info.get('count')} notes")
                
        except Exception as e:
            print(f"❌ Analytics failed: {e}")
    
    # Get recent notes
    # This method retrieves the most recent speaker notes
    def get_recent_notes(self):
        """Test recent notes functionality"""
        if not self.db_operations:
            print("❌ Database operations not initialized. Please connect first.")
            return
        
        limit = input("Enter number of recent notes (default 5): ") or "5"
        
        try:
            results = self.db_operations.get_recent_speaker_notes(limit=int(limit))
            print(f"\n🕒 {len(results)} most recent notes:")
            for i, note in enumerate(results, 1):
                print(f"{i}. {note.get('title', 'No title')} - {note.get('created_at', 'N/A')}")
        except Exception as e:
            print(f"❌ Recent notes query failed: {e}")
    
    # Test word frequency functionality
    # This method retrieves the most frequent words in speaker notes
    def get_word_frequency(self):
        """Test word frequency functionality"""
        if not self.db_operations:
            print("❌ Database operations not initialized. Please connect first.")
            return
        
        top_n = input("Enter number of top words (default 10): ") or "10"
        
        try:
            results = self.db_operations.get_word_frequency(top_n=int(top_n))
            print(f"\n🔤 Top {top_n} most frequent words:")
            for i, word_info in enumerate(results, 1):
                print(f"{i}. '{word_info.get('word')}': {word_info.get('frequency')} times")
        except Exception as e:
            print(f"❌ Word frequency analysis failed: {e}")
    
    # Test DataFrame export functionality
    # This method exports speaker notes to a Pandas DataFrame and displays it
    def export_dataframe(self):
        """Test DataFrame export functionality"""
        try:
            if not self.db_operations:
                print("❌ Database operations not initialized. Please connect first.")
                return
    
            df = self.db_operations.export_to_dataframe()
            if df is not None and not df.empty:
                print(f"\n📋 DataFrame Info:")
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print("\nFirst few rows:")
                print(df.head())
            else:
                print("❌ No data or export failed")
        except Exception as e:
            print(f"❌ DataFrame export failed: {e}")
    
    # Show main menu
    # This method displays the main menu for the operations tester
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("🚀 DUCKDB OPERATIONS TESTER")
        print("="*50)
        print("1. 🔍 Search Notes")
        print("2. 📅 Get Notes by Date Range")
        print("3. 📊 Get Analytics")
        print("4. 🕒 Get Recent Notes")
        print("5. 🔤 Get Word Frequency")
        print("6. 📋 Export to DataFrame")
        print("7. 🔄 Reconnect to Database")
        print("0. ❌ Exit")
        print("="*50)
    
    # Main execution loop
    # This method runs the operations tester, allowing users to perform various database operations
    def run(self):
        """Main execution loop"""
        print("Welcome to DuckDB Operations Tester!")
        print("🔄 Auto-connecting to database...")
        
        # Automatic connection - retry if failed
        max_retries = 3
        for attempt in range(max_retries):
            if self.connect_to_database():
                break
            elif attempt < max_retries - 1:
                print(f"🔄 Retrying connection... (Attempt {attempt + 2}/{max_retries})")
            else:
                print("❌ Failed to connect after multiple attempts. Exiting.")
                return

        # Check all current collections and their record sizes
        try:
            if not self.db_connection:
                print("❌ Database connection not established.")
                return

            mongo_db = self.db_connection.mongo_db

            if mongo_db is None:
                print("❌ MongoDB connection not established.")
                return
            
            collections = mongo_db.list_collection_names()
            if not collections:
                print("❌ No collections found in the database. Exiting.")
                if self.db_connection:
                    self.db_connection.close()
                return
            print("\n📚 Collections and record counts:")
            for coll in collections:
                count = mongo_db[coll].count_documents({})
                print(f"  - {coll}: {count} records")
        except Exception as e:
            print(f"❌ Error checking collections: {e}")
            if self.db_connection:
                self.db_connection.close()
            return

        operations = {
            '1': self.search_notes,
            '2': self.get_date_range_notes,
            '3': self.get_analytics,
            '4': self.get_recent_notes,
            '5': self.get_word_frequency,
            '6': self.export_dataframe,
            '7': self.connect_to_database,
        }
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (0-7): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                if self.db_connection:
                    self.db_connection.close()
                break
            elif choice in operations:
                print(f"\n⚡ Executing operation {choice}...")
                operations[choice]()
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    tester = OperationsTester()
    try:
        tester.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user (Ctrl+C). Exiting gracefully.")
        if tester.db_connection:
            tester.db_connection.close()
