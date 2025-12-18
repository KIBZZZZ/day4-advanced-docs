import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from text_extraction import read_document

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_for_export(text):
    """Generate a structured summary suitable for export"""
    
    text = text[:15000]
    
    prompt = """Create a structured summary of this document:

1. TITLE: A clear, descriptive title (under 10 words)
2. EXECUTIVE SUMMARY: 2-3 sentence overview
3. KEY POINTS: 5-7 bullet points of main ideas
4. DETAILS: 2-3 paragraphs of important details
5. CONCLUSION: 1-2 sentences

Format with clear section headers."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You create well-structured summaries with clear sections."},
                {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}
            ],
            temperature=0.5,
            max_tokens=600
        )
        
        summary = response.choices[0].message.content
        tokens = response.usage.total_tokens
        cost = (response.usage.prompt_tokens / 1000) * 0.00015 + \
               (response.usage.completion_tokens / 1000) * 0.0006
        
        return {
            "success": True,
            "summary": summary,
            "tokens": tokens,
            "cost": cost
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def export_as_json(summary_text, original_file, metadata):
    """Export summary as JSON"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_json_{timestamp}.json"
    
    # Parse summary sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in summary_text.split('\n'):
        line = line.strip()
        if line.endswith(':') and line.isupper():
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[:-1]
            current_content = []
        else:
            if line:
                current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Create JSON structure
    data = {
        "metadata": {
            "original_document": original_file,
            "generated": datetime.now().isoformat(),
            "tokens_used": metadata.get('tokens', 0),
            "cost": f"${metadata.get('cost', 0):.6f}"
        },
        "summary": sections,
        "full_text": summary_text
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def export_as_markdown(summary_text, original_file, metadata):
    """Export summary as Markdown"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_markdown_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Extract title
        title_line = summary_text.split('\n')[0]
        if 'TITLE:' in title_line:
            title = title_line.replace('TITLE:', '').strip()
        else:
            title = "Document Summary"
        
        f.write(f"# {title}\n\n")
        f.write(f"**Original Document:** {original_file}  \n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Processing Cost:** ${metadata.get('cost', 0):.6f}\n\n")
        f.write("---\n\n")
        
        # Convert to markdown format
        lines = summary_text.split('\n')
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                f.write('\n')
                in_list = False
                continue
            
            # Section headers
            if line.endswith(':') and (line.isupper() or line.istitle()):
                if in_list:
                    f.write('\n')
                    in_list = False
                f.write(f"## {line[:-1]}\n\n")
            # Bullet points
            elif line.startswith('-') or line.startswith('•'):
                f.write(f"{line}\n")
                in_list = True
            # Regular text
            else:
                if in_list:
                    f.write('\n')
                    in_list = False
                f.write(f"{line}\n\n")
    
    return filename

def export_as_html(summary_text, original_file, metadata):
    """Export summary as HTML"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_html_{timestamp}.html"
    
    # Extract title
    title_line = summary_text.split('\n')[0]
    if 'TITLE:' in title_line:
        title = title_line.replace('TITLE:', '').strip()
    else:
        title = "Document Summary"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        .metadata strong {{
            color: #2c3e50;
        }}
        ul {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="metadata">
            <strong>Original Document:</strong> {original_file}<br>
            <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Processing Cost:</strong> ${metadata.get('cost', 0):.6f}
        </div>
"""
    
    # Convert summary to HTML
    lines = summary_text.split('\n')
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_content += "        </ul>\n"
                in_list = False
            continue
        
        # Skip title line (already used as h1)
        if 'TITLE:' in line:
            continue
        
        # Section headers
        if line.endswith(':') and (line.isupper() or line.istitle()):
            if in_list:
                html_content += "        </ul>\n"
                in_list = False
            header = line[:-1]
            html_content += f"        <h2>{header}</h2>\n"
        # Bullet points
        elif line.startswith('-') or line.startswith('•'):
            if not in_list:
                html_content += "        <ul>\n"
                in_list = True
            item = line[1:].strip()
            html_content += f"            <li>{item}</li>\n"
        # Regular text
        else:
            if in_list:
                html_content += "        </ul>\n"
                in_list = False
            html_content += f"        <p>{line}</p>\n"
    
    if in_list:
        html_content += "        </ul>\n"
    
    html_content += """
        <div class="footer">
            Generated by AI Document Summarizer | Powered by OpenAI GPT-4o-mini
        </div>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    """Main function"""
    print("\n" + "="*70)
    print("          📤 EXPORT FORMATS SYSTEM 📤")
    print("          Export Summaries in Multiple Formats")
    print("="*70)
    
    test_folder = "test_documents"
    
    if not os.path.exists(test_folder):
        test_folder = "../day3-document-summarizer/test_documents"
        if not os.path.exists(test_folder):
            print("❌ Can't find test documents!")
            return
    
    files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
    
    if not files:
        print("❌ No files found!")
        return
    
    print(f"\n📚 Available documents:")
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    choice = input(f"\nSelect document (1-{len(files)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            print("❌ Invalid choice!")
            return
        
        selected_file = files[idx]
        file_path = os.path.join(test_folder, selected_file)
        
    except ValueError:
        print("❌ Please enter a number!")
        return
    
    # Read document
    print(f"\n📖 Reading: {selected_file}")
    doc_result = read_document(file_path)
    
    if not doc_result['success']:
        print(f"❌ Failed to read: {doc_result['error']}")
        return
    
    print(f"✅ Loaded {doc_result['word_count']} words")
    
    # Generate summary
    print("\n🔄 Generating structured summary...")
    summary_result = summarize_for_export(doc_result['text'])
    
    if not summary_result['success']:
        print(f"❌ Summarization failed: {summary_result['error']}")
        return
    
    print(f"✅ Summary generated")
    print(f"💰 Cost: ${summary_result['cost']:.6f}")
    
    # Show summary preview
    print("\n" + "┏" + "━"*68 + "┓")
    print("┃ 📄 SUMMARY PREVIEW" + " "*49 + "┃")
    print("┣" + "━"*68 + "┫")
    
    preview = summary_result['summary'][:400] + "..."
    for line in preview.split('\n'):
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
    
    print("┗" + "━"*68 + "┛")
    
    # Export options
    print("\n📤 Export formats available:")
    print("   1. JSON (for programs/APIs)")
    print("   2. Markdown (for documentation)")
    print("   3. HTML (for viewing in browser)")
    print("   4. All formats")
    
    export_choice = input("\nSelect format (1-4): ").strip()
    
    metadata = {
        'tokens': summary_result['tokens'],
        'cost': summary_result['cost']
    }
    
    exported_files = []
    
    if export_choice in ['1', '4']:
        print("\n💾 Exporting as JSON...")
        json_file = export_as_json(summary_result['summary'], selected_file, metadata)
        exported_files.append(('JSON', json_file))
        print(f"✅ Saved: {json_file}")
    
    if export_choice in ['2', '4']:
        print("\n💾 Exporting as Markdown...")
        md_file = export_as_markdown(summary_result['summary'], selected_file, metadata)
        exported_files.append(('Markdown', md_file))
        print(f"✅ Saved: {md_file}")
    
    if export_choice in ['3', '4']:
        print("\n💾 Exporting as HTML...")
        html_file = export_as_html(summary_result['summary'], selected_file, metadata)
        exported_files.append(('HTML', html_file))
        print(f"✅ Saved: {html_file}")
    
    # Summary
    if exported_files:
        print("\n" + "="*70)
        print("✅ EXPORT COMPLETE")
        print("="*70)
        print(f"Document: {selected_file}")
        print(f"Formats exported: {len(exported_files)}")
        for format_name, filename in exported_files:
            print(f"  • {format_name}: {filename}")
        print("="*70)
        
        if any('HTML' in f[0] for f in exported_files):
            print("\n💡 Tip: Open the HTML file in your browser to see the formatted summary!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted")