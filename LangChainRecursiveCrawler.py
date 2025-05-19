from langchain_community.document_loaders import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# The URL you want to crawl
start_url = "https://docs.bmc.com/xwiki/bin/view/Control-M-Orchestration/Control-M-Automation-API/ctmapi9202/Code-Reference/Job-Properties/"

# Set up the loader: max_depth controls recursion, and only_internal=True restricts to the same domain
loader = RecursiveUrlLoader(
    url=start_url,
    max_depth=2,  # Adjust as needed
    only_internal=True,
    extractor="lxml",  # Uses lxml for parsing, no browser required
)

# Load documents (this will crawl and extract text)
docs = loader.load()

# Optionally, split long documents for downstream processing
splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
splits = splitter.split_documents(docs)

# Print a summary of what was crawled
for i, doc in enumerate(splits):
    print(f"\n--- Document {i+1} ---")
    print(f"Source: {doc.metadata.get('source')}")
    print(doc.page_content[:500])  # Print first 500 chars

# Save to JSONL
jsonl_path = "crawl_output.jsonl"
with open(jsonl_path, "w", encoding="utf-8") as f_jsonl:
    for doc in splits:
        record = {
            "source": doc.metadata.get("source"),
            "content": doc.page_content,
        }
        f_jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")

# Save to Markdown
md_path = "crawl_output.md"
with open(md_path, "w", encoding="utf-8") as f_md:
    for i, doc in enumerate(splits, 1):
        source = doc.metadata.get("source", "Unknown Source")
        f_md.write(f"## Document {i}\n")
        f_md.write(f"**Source:** {source}\n\n")
        f_md.write(doc.page_content.strip() + "\n\n")
        f_md.write("---\n\n")

print(f"Saved {len(splits)} documents to {jsonl_path} and {md_path}")
