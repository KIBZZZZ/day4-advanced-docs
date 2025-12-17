import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from text_extraction import read_document

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Batch processing stats
batch_stats = {
    "total_docs": 0,
    "successful": 0,
    "failed": 0,
    "total_cost": 0.0,
    "start_time": None,
    "results": []
}

def batch_summarize(text, filename):
    """Summarize a single document in batch mode"""
    
    # Truncate if needed
    text = text[:20000]
    
    prompt = """Provide a concise summary of this document.
Include:
- Main topic (1 sentence)
- Key points (3-5 bullet points)
- Conclusion or outcome (1 sentence)

Keep it brief and clear."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You create concise, accurate summaries quickly."},
                {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}
            ],
            temperature=0.4,
            max_tokens=300
        )
        
        summary = response.choices[0].message.content
        tokens = response.usage.total_tokens
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        return {
            "success": True,
            "filename": filename,
            "summary": summary,
            "tokens": tokens,
            "cost": cost
        }
        
    except Exception as e:
        return {
            "success": False,
            "filename": filename,
            "error": str(e)
        }

def process_batch(folder_path):
    """Process all documents in a folder"""
    
    print("\n" + "="*70)
    print("🚀 BATCH PROCESSING STARTED")
    print("="*70)
    
    batch_stats["start_time"] = datetime.now()
    
    # Get all files
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    if not files:
        print(f"❌ No files found in {folder_path}")
        return
    
    batch_stats["total_docs"] = len(files)
    
    print(f"\n📚 Found {len(files)} document(s) to process")
    print(f"⏰ Started at: {batch_stats['start_time'].strftime('%H:%M:%S')}\n")
    
    # Process each document
    for i, filename in enumerate(files, 1):
        print(f"┌─ Processing {i}/{len(files)}: {filename}")
        
        file_path = os.path.join(folder_path, filename)
        
        # Read document
        doc_result = read_document(file_path)
        
        if not doc_result['success']:
            print(f"│  ❌ Failed to read: {doc_result['error']}")
            batch_stats["failed"] += 1
            batch_stats["results"].append({
                "filename": filename,
                "status": "failed",
                "error": doc_result['error']
            })
            print("└─" + "─"*66)
            continue
        
        print(f"│  📄 Read {doc_result['word_count']} words")
        
        # Summarize
        print(f"│  🔄 Generating summary...")
        summary_result = batch_summarize(doc_result['text'], filename)
        
        if summary_result['success']:
            print(f"│  ✅ Summary generated")
            print(f"│  💰 Cost: ${summary_result['cost']:.6f}")
            batch_stats["successful"] += 1
            batch_stats["total_cost"] += summary_result['cost']
            batch_stats["results"].append(summary_result)
        else:
            print(f"│  ❌ Summary failed: {summary_result['error']}")
            batch_stats["failed"] += 1
            batch_stats["results"].append({
                "filename": filename,
                "status": "failed",
                "error": summary_result['error']
            })
        
        print("└─" + "─"*66 + "\n")
    
    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - batch_stats["start_time"]).total_seconds()
    
    # Display summary
    print("\n" + "="*70)
    print("📊 BATCH PROCESSING COMPLETE")
    print("="*70)
    print(f"Total documents: {batch_stats['total_docs']}")
    print(f"Successful: {batch_stats['successful']} ✅")
    print(f"Failed: {batch_stats['failed']} ❌")
    print(f"Total cost: ${batch_stats['total_cost']:.6f}")
    print(f"Duration: {int(duration//60)}m {int(duration%60)}s")
    if batch_stats['successful'] > 0:
        avg_cost = batch_stats['total_cost'] / batch_stats['successful']
        print(f"Average cost per doc: ${avg_cost:.6f}")
    print("="*70)

def save_batch_results():
    """Save all results to a JSON file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch_results_{timestamp}.json"
    
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_documents": batch_stats["total_docs"],
            "successful": batch_stats["successful"],
            "failed": batch_stats["failed"],
            "total_cost": f"${batch_stats['total_cost']:.6f}"
        },
        "results": batch_stats["results"]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return output_file

def create_summary_report():
    """Create a readable text report of all summaries"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch_report_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("BATCH PROCESSING REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Total Documents: {batch_stats['total_docs']}\n")
        f.write(f"Successfully Processed: {batch_stats['successful']}\n")
        f.write(f"Failed: {batch_stats['failed']}\n")
        f.write(f"Total Cost: ${batch_stats['total_cost']:.6f}\n\n")
        
        f.write("="*70 + "\n\n")
        
        # Write each summary
        for i, result in enumerate(batch_stats["results"], 1):
            if result.get('success'):
                f.write(f"DOCUMENT {i}: {result['filename']}\n")
                f.write("-"*70 + "\n")
                f.write(result['summary'])
                f.write("\n")
                f.write(f"Tokens: {result['tokens']} | Cost: ${result['cost']:.6f}\n")
                f.write("="*70 + "\n\n")
            else:
                f.write(f"DOCUMENT {i}: {result['filename']}\n")
                f.write("-"*70 + "\n")
                f.write(f"❌ FAILED: {result.get('error', 'Unknown error')}\n")
                f.write("="*70 + "\n\n")
    
    return output_file

def main():
    """Main function"""
    print("\n" + "="*70)
    print("          📦 BATCH DOCUMENT PROCESSOR 📦")
    print("          Process Multiple Documents Automatically")
    print("="*70)
    
    # Get folder path
    default_folder = "test_documents"
    
    print(f"\n📁 Enter folder path to process")
    print(f"   (Press Enter to use: {default_folder})")
    
    folder = input("\nFolder path: ").strip()
    
    if not folder:
        folder = default_folder
        # Try Day 3's folder if local doesn't exist
        if not os.path.exists(folder):
            folder = "../day3-document-summarizer/test_documents"
    
    # Process batch
    process_batch(folder)
    
    # Save results
    if batch_stats["successful"] > 0 or batch_stats["failed"] > 0:
        print("\n💾 Saving results...")
        
        json_file = save_batch_results()
        print(f"✅ JSON data saved: {json_file}")
        
        report_file = create_summary_report()
        print(f"✅ Text report saved: {report_file}")
        
        print(f"\n📊 Results saved in 2 formats:")
        print(f"   - JSON (for programs): {json_file}")
        print(f"   - Text (for reading): {report_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Batch processing interrupted")
        if batch_stats["successful"] > 0 or batch_stats["failed"] > 0:
            print("Saving partial results...")
            save_batch_results()
            create_summary_report()