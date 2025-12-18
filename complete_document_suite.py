import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Import functions from other modules
from text_extraction import read_document
from batch_processor import batch_summarize, process_batch
from export_formats import export_as_json, export_as_markdown, export_as_html

# Session tracking
session = {
    "operations": 0,
    "total_cost": 0.0,
    "start_time": datetime.now()
}

def show_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("          📚 COMPLETE DOCUMENT PROCESSING SUITE 📚")
    print("="*70)
    print("\nAvailable Operations:")
    print("\n📄 SINGLE DOCUMENT:")
    print("   1. Quick Summary (executive summary)")
    print("   2. Detailed Analysis (full breakdown)")
    print("   3. Q&A Mode (ask questions about document)")
    print("   4. Export Summary (JSON/Markdown/HTML)")
    print("\n📚 MULTIPLE DOCUMENTS:")
    print("   5. Compare Two Documents")
    print("   6. Synthesize Multiple Documents")
    print("   7. Batch Process Folder")
    print("\n⚙️  SYSTEM:")
    print("   8. Show Session Statistics")
    print("   9. Exit")
    print("="*70)

def quick_summary(file_path):
    """Generate a quick executive summary"""
    print(f"\n📖 Reading document...")
    doc = read_document(file_path)
    
    if not doc['success']:
        print(f"❌ Failed: {doc['error']}")
        return
    
    print(f"✅ Loaded {doc['word_count']} words")
    print("\n🔄 Generating executive summary...")
    
    text = doc['text'][:15000]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Create concise executive summaries."},
                {"role": "user", "content": f"Provide a 2-3 paragraph executive summary:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        summary = response.choices[0].message.content
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        session['operations'] += 1
        session['total_cost'] += cost
        
        print("\n" + "┏" + "━"*68 + "┓")
        print("┃ 📄 EXECUTIVE SUMMARY" + " "*47 + "┃")
        print("┣" + "━"*68 + "┫")
        
        for line in summary.split('\n'):
            if len(line) <= 66:
                print(f"┃ {line:<66} ┃")
            else:
                words = line.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= 66:
                        current += word + " "
                    else:
                        print(f"┃ {current.rstrip():<66} ┃")
                        current = word + " "
                if current:
                    print(f"┃ {current.rstrip():<66} ┃")
        
        print("┣" + "━"*68 + "┫")
        print(f"┃ 💰 Cost: ${cost:.6f}" + " "*52 + "┃")
        print("┗" + "━"*68 + "┛")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def detailed_analysis(file_path):
    """Provide detailed document analysis"""
    print(f"\n📖 Reading document...")
    doc = read_document(file_path)
    
    if not doc['success']:
        print(f"❌ Failed: {doc['error']}")
        return
    
    print(f"✅ Loaded {doc['word_count']} words")
    print("\n🔄 Performing detailed analysis...")
    
    text = doc['text'][:15000]
    
    prompt = """Analyze this document in detail:

1. MAIN TOPIC: What is this document about?
2. KEY THEMES: What are the 3-5 main themes?
3. IMPORTANT DETAILS: List 5-7 specific details, facts, or data points
4. STRUCTURE: How is the document organized?
5. TONE & PURPOSE: What's the tone? What's the purpose?
6. ACTIONABLE INSIGHTS: What actions or decisions does this suggest?

Be specific and cite examples from the document."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a thorough document analyst."},
                {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}
            ],
            temperature=0.4,
            max_tokens=700
        )
        
        analysis = response.choices[0].message.content
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        session['operations'] += 1
        session['total_cost'] += cost
        
        print("\n" + "┏" + "━"*68 + "┓")
        print("┃ 🔍 DETAILED ANALYSIS" + " "*48 + "┃")
        print("┣" + "━"*68 + "┫")
        
        for line in analysis.split('\n'):
            if not line.strip():
                print("┃" + " "*68 + "┃")
                continue
            if len(line) <= 66:
                print(f"┃ {line:<66} ┃")
            else:
                words = line.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= 66:
                        current += word + " "
                    else:
                        print(f"┃ {current.rstrip():<66} ┃")
                        current = word + " "
                if current:
                    print(f"┃ {current.rstrip():<66} ┃")
        
        print("┣" + "━"*68 + "┫")
        print(f"┃ 💰 Cost: ${cost:.6f}" + " "*52 + "┃")
        print("┗" + "━"*68 + "┛")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_session_stats():
    """Display session statistics"""
    duration = (datetime.now() - session['start_time']).total_seconds()
    
    print("\n" + "┏" + "━"*68 + "┓")
    print("┃ 📊 SESSION STATISTICS" + " "*46 + "┃")
    print("┣" + "━"*68 + "┫")
    print(f"┃ Operations performed: {session['operations']:<47} ┃")
    print(f"┃ Total cost: ${session['total_cost']:.6f}" + " "*48 + "┃")
    print(f"┃ Session duration: {int(duration//60)}m {int(duration%60)}s" + " "*(47-len(f"{int(duration//60)}m {int(duration%60)}s")) + "┃")
    print("┗" + "━"*68 + "┛")

def select_document():
    """Helper function to select a document"""
    test_folder = "test_documents"
    
    if not os.path.exists(test_folder):
        test_folder = "../day3-document-summarizer/test_documents"
        if not os.path.exists(test_folder):
            print("❌ Can't find test documents!")
            return None
    
    files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
    
    if not files:
        print("❌ No files found!")
        return None
    
    print(f"\n📚 Available documents:")
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    choice = input(f"\nSelect document (1-{len(files)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            print("❌ Invalid choice!")
            return None
        
        return os.path.join(test_folder, files[idx])
    except ValueError:
        print("❌ Please enter a number!")
        return None

def main():
    """Main function"""
    print("\n" + "="*70)
    print("          🚀 WELCOME TO DOCUMENT PROCESSING SUITE 🚀")
    print("="*70)
    print("\nThis is your complete document processing toolkit!")
    print("All your Day 3 and Day 4 features in one place.")
    
    while True:
        show_menu()
        
        choice = input("\nSelect operation (1-9): ").strip()
        
        if choice == '1':
            file_path = select_document()
            if file_path:
                quick_summary(file_path)
        
        elif choice == '2':
            file_path = select_document()
            if file_path:
                detailed_analysis(file_path)
        
        elif choice == '3':
            print("\n💡 Q&A Mode is available in document_qa.py")
            print("   Run: python document_qa.py")
        
        elif choice == '4':
            print("\n💡 Export functionality is available in export_formats.py")
            print("   Run: python export_formats.py")
        
        elif choice == '5':
            print("\n💡 Document comparison is available in multi_doc_compare.py")
            print("   Run: python multi_doc_compare.py")
        
        elif choice == '6':
            print("\n💡 Multi-document synthesis is available in multi_doc_compare.py")
            print("   Run: python multi_doc_compare.py (choose option 2)")
        
        elif choice == '7':
            print("\n💡 Batch processing is available in batch_processor.py")
            print("   Run: python batch_processor.py")
        
        elif choice == '8':
            show_session_stats()
        
        elif choice == '9':
            show_session_stats()
            print("\n👋 Thanks for using Document Processing Suite!")
            print("="*70)
            break
        
        else:
            print("❌ Invalid choice! Please select 1-9.")
        
        input("\n👉 Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted")
        show_session_stats()