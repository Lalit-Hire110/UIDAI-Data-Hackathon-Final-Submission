"""
Experience Block 6: Insight Library
====================================
Full analytical insights from UIDAI_Master_Analysis.ipynb
All content verbatim from notebook markdown cells.
No paraphrasing, no summarization, no interpretation.
"""

import streamlit as st
from pathlib import Path

# Base path for figures
FIGURES_BASE = Path("../data/outputs/figures")


def render_insights():
    """
    Render the complete Insight Library.
    All insights verbatim from notebook "Key Insights" cells.
    """
    
    st.markdown("""
    <div style="
        text-align: center;
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <h1 style="
            color: #E6EDF3;
            font-size: 1.75rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
        ">Analytical Insights</h1>
        <p style="
            color: #8B949E;
            font-size: 0.9rem;
            margin: 0 0 0.25rem 0;
        ">Verbatim from UIDAI_Master_Analysis.ipynb</p>
        <p style="
            color: #6E7681;
            font-size: 0.75rem;
            margin: 0;
        ">All insights presented without modification or interpretation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render each domain
    render_visual_analysis_insights()
    render_demand_behavior_insights()
    render_capacity_mismatch_insights()
    render_service_quality_insights()
    render_temporal_patterns_insights()
    render_decision_matrix_insights()


def render_insight_card(number: str, title: str, content: str, implication: str):
    """Helper to render a single insight card."""
    
    st.markdown(f"""
    <div style="
        background: rgba(22, 27, 34, 0.6);
        border-left: 3px solid #1A73E8;
        border-radius: 0 8px 8px 0;
        padding: 1.25rem;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="
                color: #1A73E8;
                font-size: 0.85rem;
                font-weight: 700;
                opacity: 0.8;
            ">{number}</span>
            <h4 style="
                color: #E6EDF3;
                font-size: 0.95rem;
                font-weight: 600;
                margin: 0;
            ">{title}</h4>
        </div>
        <p style="
            color: #C9D1D9;
            font-size: 0.85rem;
            line-height: 1.6;
            margin: 0 0 0.75rem 0;
        ">{content}</p>
        <p style="
            color: #8B949E;
            font-size: 0.8rem;
            font-style: italic;
            margin: 0;
            padding-left: 1rem;
            border-left: 2px solid rgba(26, 115, 232, 0.3);
        "><strong>Implication:</strong> {implication}</p>
    </div>
    """, unsafe_allow_html=True)


def render_domain_header(domain_name: str, source: str):
    """Helper to render domain section header."""
    
    st.markdown(f"""
    <div style="
        margin: 2.5rem 0 1.5rem 0;
        padding: 1rem 0 0.75rem 0;
        border-top: 2px solid rgba(255, 153, 51, 0.3);
    ">
        <h2 style="
            color: #FF9933;
            font-size: 1.3rem;
            font-weight: 600;
            margin: 0 0 0.25rem 0;
        ">{domain_name}</h2>
        <p style="
            color: #6E7681;
            font-size: 0.7rem;
            margin: 0;
        ">Source: {source}</p>
    </div>
    """, unsafe_allow_html=True)


def render_visual_analysis_insights():
    """Domain: Visual Analytics & System Distribution"""
    
    render_domain_header(
        "Visual Analytics & System Distribution",
        "UIDAI_Master_Analysis.ipynb → Key Insights from Visual Analysis"
    )
    
    st.markdown("""
    <p style="
        color: #8B949E;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        font-style: italic;
    ">The visual analytics reveal clear and actionable patterns in Aadhaar service usage across India.</p>
    """, unsafe_allow_html=True)
    
    render_insight_card(
        "1",
        "Skewed Distribution of Service Usage",
        "The activity rate distribution shows a strong right skew, with the majority of pincodes clustered at low to moderate levels of Aadhaar activity. A long tail of higher-activity pincodes indicates that while the system performs adequately in many areas, a non-trivial subset remains significantly under-served.",
        "System-wide averages mask localized service gaps; targeted interventions are more effective than uniform expansion."
    )
    
    render_insight_card(
        "2",
        "Structural Rural–Urban Disparities",
        "The population versus activity analysis, using a logarithmic population scale, demonstrates that population size alone does not explain service usage. Rural pincodes exhibit substantially higher variance and a greater prevalence of low-activity outcomes, even at comparable population levels.",
        "Rural underperformance reflects access and infrastructure challenges rather than demographic scale alone."
    )
    
    render_insight_card(
        "3",
        "District-Level Concentration of Service Deserts",
        "Service deserts are not evenly distributed across districts. A limited number of districts account for a disproportionate share of severely underperforming rural pincodes, suggesting systemic or administrative bottlenecks at the district level.",
        "District-focused operational audits and resource allocation can yield outsized improvements."
    )
    
    render_insight_card(
        "4",
        "Actionable Priority Locations",
        "The ranked list of priority rural service desert pincodes identifies locations where low service usage coincides with substantial population exposure. These areas represent the highest-return targets for immediate intervention.",
        "Deploying mobile enrollment units, expanding enrollment centers, or targeted awareness campaigns in these pincodes can directly address critical access gaps."
    )
    
    st.markdown("""
    <p style="
        color: #9198A0;
        font-size: 0.85rem;
        margin: 1.5rem 0 0 1rem;
        padding-left: 1rem;
        border-left: 2px solid rgba(255, 255, 255, 0.1);
        line-height: 1.6;
    ">Overall, the findings indicate that Aadhaar service challenges are <strong style="color: #E6EDF3;">localized, structural, and solvable</strong> through data-driven, geographically targeted policy actions.</p>
    """, unsafe_allow_html=True)


def render_demand_behavior_insights():
    """Domain: Demand Behavior — Usage Composition"""
    
    render_domain_header(
        "Demand Behavior — Usage Composition",
        "UIDAI_Master_Analysis.ipynb → Key Insights — Demand Behavior"
    )
    
    render_insight_card(
        "1",
        "Aadhaar Usage Is Predominantly Maintenance-Driven",
        "Across a large majority of pincodes, biometric updates account for the dominant share of Aadhaar activity. This pattern reflects routine maintenance demand—such as age-based biometric refresh cycles and fingerprint degradation among senior citizens—rather than new adoption.",
        "Aadhaar infrastructure in these regions is under continuous operational stress even without population growth, requiring sustained system reliability rather than expansion alone."
    )
    
    render_insight_card(
        "2",
        "New Enrollments Are Structurally Limited in 2025",
        "Enrollment activity constitutes a small fraction of total Aadhaar usage in most regions. Where enrollments occur, they are primarily concentrated in the 0–5 age group, consistent with policy-driven restrictions on adult enrollments in 2025.",
        "Low enrollment volumes should not be interpreted as weak demand; instead, they reflect a stabilized Aadhaar base with growth driven mainly by births."
    )
    
    render_insight_card(
        "3",
        "Demographic Updates Capture Life-Event and Mobility Signals",
        "A non-trivial share of Aadhaar activity arises from demographic updates, especially address and name changes. These updates are indicative of life events such as migration, banking requirements, and marital status changes.",
        "Regions with elevated demographic update shares may benefit from targeted awareness and streamlined update services rather than enrollment expansion."
    )
    
    render_insight_card(
        "4",
        "Clean Separation Between Data Presence and Citizen Interaction",
        "No pincodes exhibit the condition where Aadhaar records are present but citizen transactions are entirely absent. This confirms that observed activity patterns reflect genuine usage behavior rather than backend reporting artifacts.",
        "Demand behavior metrics in this analysis reliably represent citizen interaction with Aadhaar services."
    )


def render_capacity_mismatch_insights():
    """Domain: Capacity Mismatch"""
    
    render_domain_header(
        "Capacity Mismatch — Demand vs Infrastructure",
        "UIDAI_Master_Analysis.ipynb → Key Insights — Capacity Mismatch"
    )
    
    render_insight_card(
        "1",
        "Aadhaar Service Stress Is Highly Localized",
        "Out of all pincodes with valid population data, approximately 1,600 exhibit significantly higher Aadhaar transaction intensity relative to their district baselines. These under-served pincodes are not randomly distributed; instead, they cluster within specific districts.",
        "Capacity constraints are localized and structural. District-focused interventions are likely to be more effective than uniform, state-wide expansion."
    )
    
    render_insight_card(
        "2",
        "Infrastructure Pressure Is Driven by Demand, Not Staffing",
        "Capacity stress reflects elevated citizen turnout interacting with limited UIDAI-issued machines (fingerprint scanners, iris devices, locked software), rather than staff shortages. This distinction is critical for designing effective operational responses.",
        "Addressing capacity mismatch requires reallocating or augmenting hardware resources, not increasing personnel alone."
    )
    
    render_insight_card(
        "3",
        "Balanced Supply Is the Norm; Oversupply Is Rare",
        "The majority of pincodes fall within a balanced range of capacity utilization, while genuinely over-served areas are relatively uncommon. This suggests that the Aadhaar system is broadly calibrated, with stress emerging only in specific high-demand pockets.",
        "Targeted redistribution of resources from balanced or over-served areas can relieve pressure without large-scale infrastructure expansion."
    )
    
    render_insight_card(
        "4",
        "Statistical Guardrails Prevent False Conclusions",
        "Pincodes lacking sufficient population comparators are explicitly flagged as having insufficient comparison context, rather than being forced into misleading classifications.",
        "Capacity assessments in this analysis are statistically conservative and avoid overstating stress where data does not support it."
    )


def render_service_quality_insights():
    """Domain: Service Quality"""
    
    render_domain_header(
        "Service Quality — Stability and Consistency",
        "UIDAI_Master_Analysis.ipynb → Key Insights — Service Quality"
    )
    
    render_insight_card(
        "1",
        "Aadhaar Service Reliability Varies Significantly Across Regions",
        "Service consistency scores reveal substantial variation in how predictably Aadhaar transactions occur over time. While a comparable share of pincodes exhibit high, moderate, and low consistency, this balance highlights that service reliability is not uniform across the country.",
        "National averages conceal meaningful local differences in Aadhaar service stability, necessitating region-aware operational planning."
    )
    
    render_insight_card(
        "2",
        "Low Consistency Reflects Irregular Demand, Not System Failure",
        "Pincodes classified as having low service consistency are characterized by fluctuating monthly activity rather than persistent absence of transactions. These fluctuations likely arise from episodic biometric refresh cycles, demographic update bursts, and scheme-driven verification surges.",
        "Low consistency should be interpreted as variable citizen interaction patterns, not as service breakdown or access denial."
    )
    
    render_insight_card(
        "3",
        "District-Level Clustering Indicates Structural Factors",
        "Districts with a high share of low-consistency pincodes tend to cluster geographically and administratively, often corresponding to remote, rural, or tribal regions. This pattern suggests that service variability is shaped by geography, mobility, and outreach dynamics rather than random noise.",
        "Improving service reliability in these districts may require adaptive delivery models, such as mobile units or scheduled service drives, rather than permanent infrastructure expansion."
    )
    
    render_insight_card(
        "4",
        "Conservative Statistical Guardrails Preserve Interpretability",
        "Pincodes lacking sufficient temporal context or district comparators are explicitly flagged as having insufficient comparison context rather than being force-classified.",
        "Service quality findings are statistically cautious and avoid overstating conclusions where data does not support reliable inference."
    )


def render_temporal_patterns_insights():
    """Domain: Temporal Patterns"""
    
    render_domain_header(
        "Temporal Patterns — Trends, Stability, and Change",
        "UIDAI_Master_Analysis.ipynb → Key Insights — Temporal Patterns"
    )
    
    render_insight_card(
        "1",
        "Aadhaar Usage Is Systematically Increasing Across Nearly All Regions",
        "The vast majority of pincodes exhibit an increasing trend in Aadhaar transaction volumes over the observed period. This pattern reflects cumulative system usage driven by biometric refresh cycles, demographic updates, and scheme-related verification requirements rather than episodic adoption.",
        "Aadhaar interaction is structurally embedded in citizen workflows, reinforcing the need for sustained operational readiness rather than short-term capacity planning."
    )
    
    render_insight_card(
        "2",
        "Declining Activity Is Rare and Localized",
        "Only a small number of pincodes show declining activity trends. These cases are isolated and do not form coherent regional clusters, suggesting localized demographic or administrative factors rather than systemic disengagement.",
        "Broad-based decline in Aadhaar usage is not evident; policy focus should remain on managing growth and variability."
    )
    
    render_insight_card(
        "3",
        "Volatility Reveals Operational Stress More Clearly Than Growth",
        "While trend slopes are largely positive, volatility scores vary substantially across districts. High-volatility districts experience sharp fluctuations in monthly activity, indicating burst-driven demand rather than steady service usage.",
        "Volatility, rather than long-term growth, is a stronger indicator of operational stress and should inform capacity planning and deployment strategies."
    )
    
    render_insight_card(
        "4",
        "Temporal Signals Reinforce Service Quality and Capacity Findings",
        "Districts with elevated volatility frequently overlap with regions identified as having low service consistency or capacity mismatch. This convergence suggests that irregular demand patterns, rather than sustained overload, are a key driver of service stress.",
        "Adaptive service models—such as mobile units, scheduled drives, or temporary capacity augmentation—are better suited than permanent infrastructure expansion in these regions."
    )


def render_decision_matrix_insights():
    """Domain: Final Decision Matrix"""
    
    render_domain_header(
        "Final Decision Matrix — Integrated Prioritization",
        "UIDAI_Master_Analysis.ipynb → Key Insights — Final Decision Matrix"
    )
    
    render_insight_card(
        "1",
        "A Tiered Priority Structure Enables Targeted Action",
        "The Decision Matrix organizes all pincodes into a clear priority hierarchy, concentrating attention on a small set of high-impact locations while maintaining broad system oversight. Only 100 pincodes are classified as critical, ensuring that operational focus remains precise and manageable.",
        "Aadhaar interventions can be planned in phases, allocating immediate resources to the most stressed locations without diluting effort across the entire system."
    )
    
    render_insight_card(
        "2",
        "High Priority Arises from Different Stress Pathways",
        "Critical and high-priority pincodes emerge due to two distinct patterns: high transaction intensity relative to population (capacity stress), and extreme temporal instability and low service consistency, even in low-population or remote areas.",
        "Priority status reflects operational risk, not population size alone. Small or remote populations can face disproportionately severe access instability that warrants attention."
    )
    
    render_insight_card(
        "3",
        "Normalized Scoring Highlights Stability Risks Beyond Volume",
        "The ranking framework intentionally relies on normalized indicators rather than absolute transaction counts. This approach ensures that service unreliability, volatility, and infrastructure strain are surfaced even when absolute usage volumes are low.",
        "Decision-makers should interpret high-priority flags in conjunction with population exposure to distinguish between large-scale demand pressure and localized service fragility."
    )
    
    render_insight_card(
        "4",
        "The Matrix Is a Decision Support Tool, Not a Prescriptive Policy",
        "The Decision Matrix does not mandate specific interventions. Instead, it provides a ranked evidence base to guide human judgment, allowing administrators to balance population impact, geographic constraints, and feasibility when planning responses.",
        "Combining quantitative prioritization with administrative discretion enables flexible, context-aware governance."
    )
