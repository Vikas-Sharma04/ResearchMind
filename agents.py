from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

# Model setup
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# 1st agent: Search agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# 2nd agent: Reader agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert research writer and technical editor.

        Produce polished, professional research reports using valid,
        well-structured Markdown.

        Formatting rules:
        1. Use # for the main title and ## for major sections.
        2. Use ### for subsections.
        3. Use **bold** for important terms and concepts.
        4. Use numbered lists for sequential procedures.
        5. Use bullet points for findings and recommendations.
        6. Use valid Markdown tables with proper header separators.
        7. Put all code inside fenced code blocks with language labels.
        8. Write mathematical equations using valid LaTeX delimiters:
           inline equations: $...$
           display equations: $$...$$
        9. Do not use malformed LaTeX, incomplete delimiters,
           HTML entities, or unnecessary HTML tags.
        10. Do not put the entire report inside a code block.
        11. Never include the prompt or instructions in the report.
        12. Do not invent facts, statistics, citations, or URLs.
        13. Preserve source URLs exactly as provided in the research.
        14. Use a clear, consistent heading hierarchy and appropriate
            spacing between sections.
        15. Convert text-based flowcharts into clear numbered steps
            or Mermaid diagrams inside fenced mermaid code blocks.
        16. Ensure every Markdown table, link, equation, and code
            block is correctly formatted.

        Return only the completed report in Markdown.
        """
    ),
    (
        "human",
        """
        Write a detailed research report on the following topic.

        # Topic
        {topic}

        # Research Material
        {research}

        Follow this report structure:

        # {topic}

        ## 1. Introduction
        Introduce the topic, its importance, and its applications.

        ## 2. Key Findings
        Present at least three detailed findings.
        Use subsections, equations, examples, or tables where useful.

        ## 3. Methodology
        Explain relevant methods and procedures step by step.

        ## 4. Technical Analysis
        Explain important models, equations, assumptions, limitations,
        and practical implementation details where relevant.

        ## 5. Conclusion
        Summarize the main findings and practical implications.

        ## 6. Sources
        List the actual URLs available in the research material.
        Do not fabricate missing URLs.

        Write an informative, factually grounded report.
        Avoid repetition and malformed formatting.
        """
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. "
        "Be honest and specific."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()