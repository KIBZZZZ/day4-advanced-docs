import os
from openai import OpenAI
from dotenv import load_dotenv
from text_extraction import read_document

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def compare_documents(doc1_text, doc2_text, doc1_name, doc2_name):
    """
    Compare two documents and identify:
    - Similarities
    - Differences
    - Unique points in each
    - Overall relationship
    """
    
    # Truncate if too long
    doc1_truncated = doc1_text[:15000]
    doc2_truncated = doc2_text[:15000]
    
    prompt = f"""Compare these two documents and provide a structured analysis:

Document 1 ({doc1_name}):
{doc1_truncated}

Document 2 ({doc2_name}):
{doc2_truncated}

Provide analysis in this format:

SIMILARITIES:
- List 3-5 key similarities or overlapping themes

DIFFERENCES:
- List 3-5 key differences in content, tone, or focus

UNIQUE TO DOCUMENT 1:
- 2-3 points only found in document 1

UNIQUE TO DOCUMENT 2:
- 2-3 points only found in document 2

RELATIONSHIP:
- How do these documents relate? (complementary, contradictory, independent, etc.)

SUMMARY:
- One paragraph summarizing the comparison"""

    print("\n🔄 Comparing documents...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert document analyst who compares documents precisely and identifies key relationships."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        comparison = response.choices[0].message.content
        tokens = response.usage.total_tokens
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        return {
            "success": True,
            "comparison": comparison,
            "tokens": tokens,
            "cost": cost
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def synthesize_multiple_docs(documents):
    """
    Synthesize information from 3+ documents into one coherent summary
    """
    
    # Create combined text with labels
    combined = ""
    for i, (name, text) in enumerate(documents, 1):
        truncated = text[:8000]  # Limit each doc
        combined += f"\n\n=== DOCUMENT {i}: {name} ===\n{truncated}\n"
    
    prompt = f"""Analyze these multiple documents and create a synthesis:

{combined}

Provide:

MAIN THEMES:
- Identify 3-5 overarching themes across all documents

KEY INSIGHTS BY DOCUMENT:
- 1-2 key points from each document

CONNECTIONS:
- How do these documents relate to each other?
- What story do they tell together?

SYNTHESIS SUMMARY:
- 2-3 paragraphs synthesizing all documents into a coherent narrative"""

    print(f"\n🔄 Synthesizing {len(documents)} documents...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You synthesize information from multiple documents, finding connections and creating unified narratives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        synthesis = response.choices[0].message.content
        tokens = response.usage.total_tokens
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        return {
            "success": True,
            "synthesis": synthesis,
            "tokens": tokens,
            "cost": cost
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def display_comparison(result, doc1_name, doc2_name):
    """Display comparison in formatted output"""
    if not result['success']:
        print(f"\n❌ Error: {result['error']}")
        return
    
    print("\n" + "┏" + "━"*68 + "┓")
    print(f"┃ 🔍 DOCUMENT COMPARISON" + " "*45 + "┃")
    print("┣" + "━"*68 + "┫")
    print(f"┃ Doc 1: {doc1_name[:60]:<60} ┃")
    print(f"┃ Doc 2: {doc2_name[:60]:<60} ┃")
    print("┣" + "━"*68 + "┫")
    
    # Display comparison with wrapping
    lines = result['comparison'].split('\n')
    for line in lines:
        if not line.strip():
            print("┃" + " "*68 + "┃")
            continue
        
        if len(line) <= 66:
            print(f"┃ {line:<66} ┃")
        else:
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= 66:
                    current_line += word + " "
                else:
                    print(f"┃ {current_line.rstrip():<66} ┃")
                    current_line = word + " "
            if current_line:
                print(f"┃ {current_line.rstrip():<66} ┃")
    
    print("┣" + "━"*68 + "┫")
    print(f"┃ 📊 Tokens: {result['tokens']:<10} | 💰 Cost: ${result['cost']:.6f}" + " "*25 + "┃")
    print("┗" + "━"*68 + "┛")

def display_synthesis(result, doc_count):
    """Display synthesis result"""
    if not result['success']:
        print(f"\n❌ Error: {result['error']}")
        return
    
    print("\n" + "┏" + "━"*68 + "┓")
    print(f"┃ 🔗 MULTI-DOCUMENT SYNTHESIS ({doc_count} documents)" + " "*(33-len(str(doc_count))) + "┃")
    print("┣" + "━"*68 + "┫")
    
    lines = result['synthesis'].split('\n')
    for line in lines:
        if not line.strip():
            print("┃" + " "*68 + "┃")
            continue
        
        if len(line) <= 66:
            print(f"┃ {line:<66} ┃")
        else:
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= 66:
                    current_line += word + " "
                else:
                    print(f"┃ {current_line.rstrip():<66} ┃")
                    current_line = word + " "
            if current_line:
                print(f"┃ {current_line.rstrip():<66} ┃")
    
    print("┣" + "━"*68 + "┫")
    print(f"┃ 📊 Tokens: {result['tokens']:<10} | 💰 Cost: ${result['cost']:.6f}" + " "*25 + "┃")
    print("┗" + "━"*68 + "┛")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("          🔍 MULTI-DOCUMENT COMPARISON TOOL 🔍")
    print("="*70)
    
    test_folder = "test_documents"
    
    if not os.path.exists(test_folder):
        print(f"\n❌ Folder not found: {test_folder}")
        print("   Using Day 3's test_documents folder...")
        test_folder = "../day3-document-summarizer/test_documents"
        
        if not os.path.exists(test_folder):
            print("❌ Can't find test documents!")
            return
    
    files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
    
    if len(files) < 2:
        print(f"\n❌ Need at least 2 documents for comparison!")
        return
    
    print(f"\n📚 Available documents ({len(files)} found):")
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    print("\n📋 Choose operation:")
    print("   1. Compare two documents")
    print("   2. Synthesize multiple documents (3+)")
    
    operation = input("\nSelect operation (1 or 2): ").strip()
    
    if operation == "1":
        # Two-document comparison
        doc1_choice = input(f"\nSelect first document (1-{len(files)}): ").strip()
        doc2_choice = input(f"Select second document (1-{len(files)}): ").strip()
        
        try:
            idx1 = int(doc1_choice) - 1
            idx2 = int(doc2_choice) - 1
            
            if idx1 < 0 or idx1 >= len(files) or idx2 < 0 or idx2 >= len(files):
                print("❌ Invalid selection!")
                return
            
            if idx1 == idx2:
                print("❌ Please select two different documents!")
                return
            
            file1 = files[idx1]
            file2 = files[idx2]
            path1 = os.path.join(test_folder, file1)
            path2 = os.path.join(test_folder, file2)
            
        except ValueError:
            print("❌ Please enter numbers!")
            return
        
        # Read documents
        print(f"\n📖 Reading documents...")
        
        result1 = read_document(path1)
        result2 = read_document(path2)
        
        if not result1['success'] or not result2['success']:
            print("❌ Failed to read one or both documents!")
            return
        
        print(f"✅ Loaded: {file1} ({result1['word_count']} words)")
        print(f"✅ Loaded: {file2} ({result2['word_count']} words)")
        
        # Compare
        comparison_result = compare_documents(
            result1['text'], 
            result2['text'],
            file1,
            file2
        )
        
        display_comparison(comparison_result, file1, file2)
        
        # Save option
        if comparison_result['success']:
            save = input("\n💾 Save comparison? (y/n): ").strip().lower()
            if save == 'y':
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = f"comparison_{timestamp}.txt"
                
                with open(output, 'w', encoding='utf-8') as f:
                    f.write("="*70 + "\n")
                    f.write("DOCUMENT COMPARISON\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*70 + "\n\n")
                    f.write(f"Document 1: {file1}\n")
                    f.write(f"Document 2: {file2}\n\n")
                    f.write("-"*70 + "\n\n")
                    f.write(comparison_result['comparison'])
                    f.write("\n\n" + "="*70 + "\n")
                    f.write(f"Cost: ${comparison_result['cost']:.6f}\n")
                
                print(f"✅ Saved to: {output}")
    
    elif operation == "2":
        # Multi-document synthesis
        print("\nSelect documents to synthesize (enter numbers separated by commas)")
        print("Example: 1,2,3")
        
        selections = input(f"\nEnter document numbers: ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selections.split(',')]
            
            if len(indices) < 3:
                print("❌ Please select at least 3 documents for synthesis!")
                return
            
            if any(i < 0 or i >= len(files) for i in indices):
                print("❌ Invalid document number!")
                return
            
            documents = []
            
            print(f"\n📖 Loading {len(indices)} documents...")
            
            for idx in indices:
                file = files[idx]
                path = os.path.join(test_folder, file)
                result = read_document(path)
                
                if result['success']:
                    documents.append((file, result['text']))
                    print(f"✅ Loaded: {file}")
                else:
                    print(f"❌ Failed to load: {file}")
            
            if len(documents) < 3:
                print("❌ Not enough documents loaded successfully!")
                return
            
            # Synthesize
            synthesis_result = synthesize_multiple_docs(documents)
            display_synthesis(synthesis_result, len(documents))
            
            # Save option
            if synthesis_result['success']:
                save = input("\n💾 Save synthesis? (y/n): ").strip().lower()
                if save == 'y':
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output = f"synthesis_{timestamp}.txt"
                    
                    with open(output, 'w', encoding='utf-8') as f:
                        f.write("="*70 + "\n")
                        f.write("MULTI-DOCUMENT SYNTHESIS\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*70 + "\n\n")
                        f.write(f"Documents synthesized: {len(documents)}\n")
                        for name, _ in documents:
                            f.write(f"  - {name}\n")
                        f.write("\n" + "-"*70 + "\n\n")
                        f.write(synthesis_result['synthesis'])
                        f.write("\n\n" + "="*70 + "\n")
                        f.write(f"Cost: ${synthesis_result['cost']:.6f}\n")
                    
                    print(f"✅ Saved to: {output}")
        
        except ValueError:
            print("❌ Please enter valid numbers separated by commas!")
            return
    
    else:
        print("❌ Invalid operation!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted")