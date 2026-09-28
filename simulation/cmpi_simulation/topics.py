"""Topic catalogue: the 20 fictional story angles backing the synthetic corpora.

Structure: CATALOGUE[day_type] is a list of 10 dicts, one per ground-truth cluster.
Each dict carries:
    - cluster_index: int (0..9)
    - protagonist: bool
    - parent_event: str  (currently always "none" — every cluster is an independent story
       on both day types in the present design; the field is reserved for a future variant
       of the catalogue in which several clusters share an overarching event)
    - theme: str  (defence, diplomacy, economy, sport, weather, etc.)
    - story_angle: str  (a one-line scene description for prompting the LLM)
    - sub_story_focus: str | None  (currently always None for the same reason as parent_event;
       reserved for marking sub-stories of a shared parent event in a future variant)
"""

CATALOGUE = {
    "low_cmpi": [
        # Protagonist cluster 1: defence package announcement (size 25)
        {
            "cluster_index": 0,
            "protagonist": True,
            "parent_event": "none",
            "theme": "defence",
            "story_angle": "Veridia's prime minister announces a 1.4 billion euro multi-year defence procurement package covering air defence and naval patrol vessels.",
            "sub_story_focus": None,
        },
        # Protagonist cluster 2: diplomatic visit (size 15)
        {
            "cluster_index": 1,
            "protagonist": True,
            "parent_event": "none",
            "theme": "diplomacy",
            "story_angle": "Veridia's prime minister visits Latvia for trilateral talks on Baltic security cooperation and energy infrastructure.",
            "sub_story_focus": None,
        },
        # Non-protagonist clusters with thematic overlap
        {
            "cluster_index": 2,
            "protagonist": False,
            "parent_event": "none",
            "theme": "defence",
            "story_angle": "NATO finalises a multi-country procurement deal for air-defence missiles, with deliveries to begin next spring.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 3,
            "protagonist": False,
            "parent_event": "none",
            "theme": "diplomacy",
            "story_angle": "EU foreign ministers meet in Brussels to coordinate a fresh package of sanctions on a third-country regime.",
            "sub_story_focus": None,
        },
        # Non-protagonist clusters on distinct themes
        {
            "cluster_index": 4,
            "protagonist": False,
            "parent_event": "none",
            "theme": "economy",
            "story_angle": "Brent crude prices fall sharply on weakened demand outlook and an unexpected inventory build in the United States.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 5,
            "protagonist": False,
            "parent_event": "none",
            "theme": "weather",
            "story_angle": "Wildfires spread across two regions of southern Greece, prompting evacuations of three coastal villages and an EU civil-protection request.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 6,
            "protagonist": False,
            "parent_event": "none",
            "theme": "sport",
            "story_angle": "A new world record is set in the women's 1500 metres at an athletics meet in Zurich, breaking a mark that had stood for fifteen years.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 7,
            "protagonist": False,
            "parent_event": "none",
            "theme": "technology",
            "story_angle": "A major European chip manufacturer announces a new fabrication plant in Saxony, supported by state and EU subsidies.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 8,
            "protagonist": False,
            "parent_event": "none",
            "theme": "health",
            "story_angle": "European regulators approve a new long-acting injectable treatment for HIV prevention, with rollout expected by mid-year.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 9,
            "protagonist": False,
            "parent_event": "none",
            "theme": "culture",
            "story_angle": "A long-lost manuscript by a 19th-century Polish poet is discovered in the archives of a Vienna library.",
            "sub_story_focus": None,
        },
    ],
    "high_cmpi": [
        # Eight topically-independent protagonist stories: a busy news day where Norvik
        # appears in many distinct narratives. No shared parent event — each cluster has
        # its own vocabulary and entities so that a fixed-threshold clusterer can recover
        # them cleanly.
        {
            "cluster_index": 0,
            "protagonist": True,
            "parent_event": "none",
            "theme": "defence",
            "story_angle": "Veridia's prime minister presents the annual defence budget statement in parliament, reaffirming the 2.7% GDP target.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 1,
            "protagonist": True,
            "parent_event": "none",
            "theme": "diplomacy",
            "story_angle": "Veridia's prime minister begins a working visit to Lithuania for talks on a new Baltic energy corridor.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 2,
            "protagonist": True,
            "parent_event": "none",
            "theme": "economy",
            "story_angle": "Veridia's prime minister addresses the Veridian Business Federation on the inflation outlook and a planned wage-tax review.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 3,
            "protagonist": True,
            "parent_event": "none",
            "theme": "regional",
            "story_angle": "Veridia's prime minister visits flood-affected Vidlands province and announces a 200 million euro emergency-relief package.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 4,
            "protagonist": True,
            "parent_event": "none",
            "theme": "ceremonial",
            "story_angle": "Veridia's prime minister attends the state funeral of a neighbouring head of state and signs the official condolence book.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 5,
            "protagonist": True,
            "parent_event": "none",
            "theme": "education",
            "story_angle": "Veridia's prime minister launches a national STEM-scholarship programme at the University of Verithall.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 6,
            "protagonist": True,
            "parent_event": "none",
            "theme": "infrastructure",
            "story_angle": "Veridia's prime minister inaugurates the new Verithall to Stamvik high-speed rail line at a ceremony at Verithall Central station.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 7,
            "protagonist": True,
            "parent_event": "none",
            "theme": "security",
            "story_angle": "Veridia's prime minister gives a press conference on a state-actor cyberattack against the Veridian Health Ministry.",
            "sub_story_focus": None,
        },
        # Two large non-protagonist clusters (unchanged).
        {
            "cluster_index": 8,
            "protagonist": False,
            "parent_event": "none",
            "theme": "defence",
            "story_angle": "A separate NATO summit on Baltic-Sea undersea-cable security goes ahead in Helsinki.",
            "sub_story_focus": None,
        },
        {
            "cluster_index": 9,
            "protagonist": False,
            "parent_event": "none",
            "theme": "diplomacy",
            "story_angle": "EU foreign ministers convene in Luxembourg for an extraordinary session on a Mediterranean migration accord with North African partners.",
            "sub_story_focus": None,
        },
    ],
}
