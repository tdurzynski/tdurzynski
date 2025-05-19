import json
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

start_url = "https://docs.bmc.com/xwiki/bin/view/Control-M-Orchestration/Control-M-Automation-API/ctmapi9202/Code-Reference/Job-Properties/"

def lxml_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    main = soup.find("div", id="xwikicontent")
    if not main:
        return soup.get_text(separator="\n")

    content_lines = []
    # Iterate through all descendants of the main content div
    for elem in main.descendants:
        if not hasattr(elem, "name"):
            continue
        # Extract code blocks
        if elem.name == "div" and "code" in elem.get("class", []):
            code_text = elem.get_text(separator="\n").strip()
            if code_text:
                content_lines.append(f"\n```text\n{code_text}\n```")
        # Extract paragraphs
        elif elem.name == "p":
            p_text = elem.get_text(separator="\n").strip()
            if p_text:
                content_lines.append(p_text)
        # Extract lists
        elif elem.name in ["ul", "ol"]:
            items = [li.get_text(separator=" ").strip() for li in elem.find_all("li")]
            if items:
                content_lines.append("\n".join(f"- {item}" for item in items))
        # Extract tables
        elif elem.name == "table":
            rows = []
            for tr in elem.find_all("tr"):
                cells = [td.get_text(separator=" ").strip() for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(" | ".join(cells))
            if rows:
                content_lines.append("\n".join(rows))
    # Join all extracted content, preserving order
    return "\n\n".join(content_lines)

loader = RecursiveUrlLoader(
    url=start_url,
    max_depth=2,
    prevent_outside=True,
    extractor=lxml_extractor,
)

docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
splits = splitter.split_documents(docs)

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
