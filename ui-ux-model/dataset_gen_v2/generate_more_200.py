"""Generate 200 more unique Forma v2 records (IDs 101-300). Distinct from first 100."""

from __future__ import annotations
import argparse, json
from pathlib import Path
from generate_unique_100 import (
    ARCHETYPE_GENERATORS, NAV_PATTERNS, INTERACTION_MODELS,
    RESPONSIVE_STRATEGIES, RADIUS_LANGUAGE, SPACING_RHYTHMS,
    _null_viewport, _components_for_archetype,
)

NAMESPACE = "forma_single"

NEW_PRODUCTS = [
    {"id": "101", "category": "ecommerce", "brand": "Loom & Lark", "goal": "help a gift buyer find a handmade ceramic gift by recipient personality and budget", "audience": "gift buyers who dislike generic options", "page_type": "gift finder quiz"},
    {"id": "102", "category": "ecommerce", "brand": "Peak Outfitters", "goal": "help a hiker find correctly sized gear for tall and plus-size bodies", "audience": "tall and plus-size hikers", "page_type": "size-fit recommender"},
    {"id": "103", "category": "subscription", "brand": "Bloombox", "goal": "let a subscriber pause, skip, or swap their monthly flower delivery", "audience": "flower subscribers with changing schedules", "page_type": "subscription management portal"},
    {"id": "104", "category": "marketplace", "brand": "Rewear", "goal": "let a user swap used clothing for credit toward other listings", "audience": "eco-conscious fashion swappers aged 18-34", "page_type": "swap credit dashboard"},
    {"id": "105", "category": "ecommerce", "brand": "Spice Route", "goal": "help a home cook discover spice blend pairings for their pantry ingredients", "audience": "adventurous home cooks", "page_type": "flavor pairing explorer"},
    {"id": "106", "category": "marketplace", "brand": "Vinyl Vault", "goal": "help a collector judge a used vinyl grading and preview audio clips", "audience": "vinyl collectors wary of overgrading", "page_type": "vinyl detail with audio preview"},
    {"id": "107", "category": "ecommerce", "brand": "Petal & Post", "goal": "help a last-minute giver track same-day flower delivery hour by hour", "audience": "last-minute gift givers", "page_type": "delivery tracking checkout"},
    {"id": "108", "category": "marketplace", "brand": "Toolshare", "goal": "let a DIYer borrow neighborhood tools with availability calendar", "audience": "urban DIYers without storage", "page_type": "lending catalog with calendar"},
    {"id": "109", "category": "ecommerce", "brand": "Kicks Custom", "goal": "let a sneaker fan design a custom colorway with live 3D preview", "audience": "sneaker fans who want one-of-ones", "page_type": "3D customizer studio"},
    {"id": "110", "category": "ecommerce", "brand": "Tea Terra", "goal": "help a tea beginner build a tasting flight by flavor intensity", "audience": "tea beginners overwhelmed by varieties", "page_type": "tasting flight builder"},
    {"id": "111", "category": "ecommerce", "brand": "Bright Baby", "goal": "help new parents compare baby gear on safety ratings and recalls", "audience": "first-time parents prioritizing safety", "page_type": "safety comparison table"},
    {"id": "112", "category": "ecommerce", "brand": "Frame & Pine", "goal": "let an art owner visualize custom framing on their wall photo", "audience": "art owners framing prints at home", "page_type": "frame visualizer"},
    {"id": "113", "category": "retail", "brand": "Bulk Haven", "goal": "help a zero-waste shopper find refill stations with live inventory", "audience": "zero-waste shoppers in cities", "page_type": "refill station map"},
    {"id": "114", "category": "marketplace", "brand": "Gamer Chest", "goal": "help a retro gamer estimate trade-in value from cartridge condition", "audience": "retro gamers trading collections", "page_type": "trade-in estimator"},
    {"id": "115", "category": "ecommerce", "brand": "Linen Loft", "goal": "help a hot sleeper choose bedding by breathability quiz", "audience": "hot sleepers seeking cool bedding", "page_type": "material guide quiz"},
    {"id": "116", "category": "subscription", "brand": "Plant Parent", "goal": "help a beginner plant owner build a care kit by light and pets", "audience": "beginner plant owners with pets", "page_type": "care kit builder"},
    {"id": "117", "category": "marketplace", "brand": "Moto Market", "goal": "help a buyer review motorcycle history and book inspection", "audience": "used motorcycle buyers", "page_type": "vehicle history detail"},
    {"id": "118", "category": "ecommerce", "brand": "Craft Crate", "goal": "help a parent match craft kits to a child's age and mess tolerance", "audience": "parents of kids aged 3-8", "page_type": "age-match finder"},
    {"id": "119", "category": "ecommerce", "brand": "Espresso Gear", "goal": "help a home barista compare espresso machines with brew cost calculator", "audience": "home baristas upgrading setup", "page_type": "machine comparison with calculator"},
    {"id": "120", "category": "marketplace", "brand": "Second Cycle", "goal": "help a commuter find a refurbished bike with fit calculator", "audience": "bike commuters on a budget", "page_type": "bike fit plus listing search"},
    {"id": "121", "category": "saas", "brand": "Flowstate", "goal": "help a remote team lead read async standups without meeting overload", "audience": "remote team leads with 8+ reports", "page_type": "standup timeline feed"},
    {"id": "122", "category": "saas", "brand": "Budgetly Teams", "goal": "help a finance operator approve team spend with policy flags", "audience": "finance operators at startups", "page_type": "approval inbox"},
    {"id": "123", "category": "saas", "brand": "Churnguard", "goal": "help a CS manager spot churn-risk accounts and assign plays", "audience": "customer success managers", "page_type": "risk scoring table"},
    {"id": "124", "category": "devtools", "brand": "Launchpad", "goal": "help an engineer monitor feature flag rollouts and kill bad releases", "audience": "engineers owning releases", "page_type": "flag rollout dashboard"},
    {"id": "125", "category": "saas", "brand": "Hireloop", "goal": "help a hiring manager compare interview scorecards fairly", "audience": "hiring managers running panels", "page_type": "scorecard comparison view"},
    {"id": "126", "category": "saas", "brand": "Inkline", "goal": "help a legal ops coordinator track e-signature status across signers", "audience": "legal ops coordinators", "page_type": "signature status tracker"},
    {"id": "127", "category": "devtools", "brand": "Cacheview", "goal": "help a platform engineer see CDN cache hit rates by edge region", "audience": "platform engineers debugging latency", "page_type": "cache analytics dashboard"},
    {"id": "128", "category": "devtools", "brand": "Oncallly", "goal": "help an SRE balance on-call load and see burnout risk", "audience": "SREs managing rotations", "page_type": "rotation calendar with load view"},
    {"id": "129", "category": "saas", "brand": "Surveystack", "goal": "help a researcher cluster open-ended survey answers into themes", "audience": "UX researchers with 1000+ responses", "page_type": "response cluster explorer"},
    {"id": "130", "category": "saas", "brand": "Assetgrid", "goal": "help a designer track asset versions and approvals", "audience": "brand designers in review cycles", "page_type": "asset version timeline"},
    {"id": "131", "category": "saas", "brand": "Timefence", "goal": "help an agency owner approve contractor timesheets quickly", "audience": "agency owners with hourly contractors", "page_type": "timesheet approval board"},
    {"id": "132", "category": "saas", "brand": "Knowledge Nest", "goal": "help an ops lead audit stale internal wiki pages", "audience": "ops leads owning documentation", "page_type": "wiki health dashboard"},
    {"id": "133", "category": "devtools", "brand": "Apicheck", "goal": "help a developer see synthetic API checks on a world map", "audience": "developers owning uptime", "page_type": "synthetic check map"},
    {"id": "134", "category": "saas", "brand": "Sprintly", "goal": "help a scrum master see burndown with scope-change overlay", "audience": "scrum masters mid-sprint", "page_type": "burndown chart view"},
    {"id": "135", "category": "saas", "brand": "Feedback Farm", "goal": "help a PM let users vote on feedback without duplicate chaos", "audience": "PMs triaging feature requests", "page_type": "feedback voting board"},
    {"id": "136", "category": "devtools", "brand": "Envault", "goal": "help a security engineer track secrets due for rotation", "audience": "security engineers", "page_type": "secrets rotation table"},
    {"id": "137", "category": "saas", "brand": "Meetless", "goal": "help a manager see meeting costs and decline low-value invites", "audience": "managers drowning in meetings", "page_type": "cost calculator dashboard"},
    {"id": "138", "category": "saas", "brand": "Translate Hub", "goal": "help a localization manager track string coverage per locale", "audience": "localization managers", "page_type": "locale progress matrix"},
    {"id": "139", "category": "devtools", "brand": "Testpilot", "goal": "help a QA engineer spot flaky tests in a heatmap", "audience": "QA engineers triaging CI", "page_type": "flakiness heatmap"},
    {"id": "140", "category": "saas", "brand": "Datawise", "goal": "help a privacy officer process GDPR deletion requests on time", "audience": "privacy officers", "page_type": "deletion request queue"},
    {"id": "141", "category": "devtools", "brand": "Promptdeck", "goal": "help an AI engineer version prompts and compare outputs", "audience": "AI engineers iterating prompts", "page_type": "prompt version gallery"},
    {"id": "142", "category": "saas", "brand": "Offboard", "goal": "help HR run a humane offboarding checklist with asset return", "audience": "HR generalists", "page_type": "offboarding stepper"},
    {"id": "143", "category": "saas", "brand": "Invoice Ally", "goal": "help a freelancer automate late-payment nudges politely", "audience": "freelancers chasing invoices", "page_type": "nudge automation flow"},
    {"id": "144", "category": "saas", "brand": "Roadmap Radio", "goal": "help users vote on a public roadmap tied to changelog", "audience": "engaged product users", "page_type": "roadmap timeline with voting"},
    {"id": "145", "category": "saas", "brand": "Standby", "goal": "help an eng manager track incident retro actions to done", "audience": "engineering managers post-incident", "page_type": "retro action kanban"},
    {"id": "146", "category": "saas", "brand": "Linkly", "goal": "help a marketer govern UTM links and stop typos", "audience": "growth marketers", "page_type": "link governance table"},
    {"id": "147", "category": "saas", "brand": "Privy Docs", "goal": "help IT approve app access requests with context", "audience": "IT admins", "page_type": "access approval inbox"},
    {"id": "148", "category": "saas", "brand": "Cohortly", "goal": "help a lifecycle marketer see onboarding email performance by cohort", "audience": "lifecycle marketers", "page_type": "cohort performance grid"},
    {"id": "149", "category": "devtools", "brand": "Schemadiff", "goal": "help a backend dev preview DB migrations before applying", "audience": "backend developers", "page_type": "migration diff viewer"},
    {"id": "150", "category": "productivity", "brand": "Quiet Hours", "goal": "help an employee batch notifications into focus-friendly digests", "audience": "employees with notification fatigue", "page_type": "notification preference center"},
    {"id": "151", "category": "healthcare", "brand": "Derma Scan", "goal": "help an adult triage a concerning mole photo before clinic visit", "audience": "adults noticing skin changes", "page_type": "photo triage flow"},
    {"id": "152", "category": "healthcare", "brand": "Pill Pal", "goal": "help a patient manage refills and check drug interactions", "audience": "patients on 4+ medications", "page_type": "refill dashboard with checker"},
    {"id": "153", "category": "mental health", "brand": "Mind Garden", "goal": "guide an anxious adult through CBT journaling prompts", "audience": "adults managing anxiety", "page_type": "guided journal editor"},
    {"id": "154", "category": "healthcare", "brand": "Physio Path", "goal": "guide a knee-surgery patient through rehab videos safely", "audience": "post-surgery rehab patients", "page_type": "rehab exercise player"},
    {"id": "155", "category": "healthcare", "brand": "Glucose Guide", "goal": "show a prediabetic how meals spike glucose on a timeline", "audience": "prediabetics with CGM", "page_type": "meal-impact timeline"},
    {"id": "156", "category": "wellness", "brand": "Sleep Stack", "goal": "help a poor sleeper correlate snoring with sleep stages", "audience": "adults tracking sleep quality", "page_type": "sleep correlation dashboard"},
    {"id": "157", "category": "healthcare", "brand": "Dental Due", "goal": "help a family schedule dental recalls without phone tag", "audience": "busy families with kids", "page_type": "family recall calendar"},
    {"id": "158", "category": "healthcare", "brand": "Allergy Atlas", "goal": "help an allergy sufferer link symptoms to pollen counts", "audience": "seasonal allergy sufferers", "page_type": "symptom versus pollen chart"},
    {"id": "159", "category": "healthcare", "brand": "Postpartum Bloom", "goal": "help a new mother check in and find support resources", "audience": "new mothers in first 12 weeks", "page_type": "check-in flow with resources"},
    {"id": "160", "category": "telehealth", "brand": "Vision Check", "goal": "let a remote patient run a visual acuity screener at home", "audience": "remote patients needing triage", "page_type": "acuity test interface"},
    {"id": "161", "category": "healthcare", "brand": "Migraine Map", "goal": "help a migraineur spot triggers with weather overlay", "audience": "people with chronic migraine", "page_type": "trigger diary with overlay"},
    {"id": "162", "category": "nutrition", "brand": "Ironclad", "goal": "help an anemic patient plan iron-rich meals simply", "audience": "patients with iron deficiency", "page_type": "meal planner with tracker"},
    {"id": "163", "category": "healthcare", "brand": "Hearing Help", "goal": "help a senior compare hearing aids and book a trial", "audience": "seniors with hearing loss", "page_type": "aid comparison plus trial flow"},
    {"id": "164", "category": "healthcare", "brand": "Vaccinetrack", "goal": "help parents track family immunizations across clinics", "audience": "parents managing kids records", "page_type": "immunization timeline"},
    {"id": "165", "category": "wellness", "brand": "Back Ease", "goal": "coach an office worker through posture micro-breaks", "audience": "desk workers with back pain", "page_type": "break coach with timer"},
    {"id": "166", "category": "fitness", "brand": "Hydra", "goal": "help an athlete adjust hydration goals to heat and sweat", "audience": "endurance athletes", "page_type": "hydration tracker"},
    {"id": "167", "category": "fitness", "brand": "Cycle Sync", "goal": "help an athlete adapt training to cycle phase", "audience": "menstruating athletes", "page_type": "phase-adaptive planner"},
    {"id": "168", "category": "fitness", "brand": "Senior Steps", "goal": "guide seniors through fall-prevention balance routines", "audience": "seniors aged 70-plus", "page_type": "balance program player"},
    {"id": "169", "category": "wellness", "brand": "Breathwork Pro", "goal": "help a freediver build CO2 tolerance safely", "audience": "freedivers training dry", "page_type": "tolerance training timer"},
    {"id": "170", "category": "nutrition", "brand": "Gutcheck", "goal": "help an IBS patient run a FODMAP elimination diary", "audience": "IBS patients in elimination phase", "page_type": "elimination diary"},
    {"id": "171", "category": "education", "brand": "Math Meadows", "goal": "teach fractions to 3rd graders through a game story", "audience": "kids aged 8-9", "page_type": "game lesson player"},
    {"id": "172", "category": "education", "brand": "Thesis Ally", "goal": "help a grad student map citation relationships visually", "audience": "grad students writing lit reviews", "page_type": "citation graph workspace"},
    {"id": "173", "category": "education", "brand": "Sign Speak", "goal": "help an ASL learner find signs by handshape video", "audience": "beginner ASL learners", "page_type": "video dictionary search"},
    {"id": "174", "category": "education", "brand": "Orchestra Audition", "goal": "help a music student practice excerpts with metronome", "audience": "music students auditioning", "page_type": "excerpt practice player"},
    {"id": "175", "category": "education", "brand": "Driverly", "goal": "help a teen log supervised drives for license hours", "audience": "teen drivers and parents", "page_type": "drive log with sign-off"},
    {"id": "176", "category": "education", "brand": "Med Mnemonics", "goal": "help med students retain anatomy via spaced mnemonics", "audience": "first-year med students", "page_type": "mnemonic deck player"},
    {"id": "177", "category": "education", "brand": "Grant Guru", "goal": "help researchers track grant deadlines and requirements", "audience": "academic grant seekers", "page_type": "deadline kanban"},
    {"id": "178", "category": "education", "brand": "Chess Coach", "goal": "help a club player climb tactics by rating ladder", "audience": "intermediate chess players", "page_type": "puzzle ladder interface"},
    {"id": "179", "category": "education", "brand": "Language Table", "goal": "match language learners for conversation exchange", "audience": "adult language learners", "page_type": "exchange matcher"},
    {"id": "180", "category": "education", "brand": "Lab Safety", "goal": "ensure undergrads pass chem pre-lab safety checks", "audience": "undergrad chemistry students", "page_type": "safety checklist stepper"},
    {"id": "181", "category": "education", "brand": "Portfolio Prep", "goal": "help art applicants track portfolio deadlines and pieces", "audience": "high-school artists applying", "page_type": "application tracker"},
    {"id": "182", "category": "education", "brand": "Debate Deck", "goal": "help debaters build cases with evidence cards", "audience": "high-school debaters", "page_type": "case builder"},
    {"id": "183", "category": "education", "brand": "Farm School", "goal": "teach kids crop lifecycles through simulation", "audience": "kids aged 6-10", "page_type": "lifecycle simulation"},
    {"id": "184", "category": "education", "brand": "Bar Exam Buddy", "goal": "show law grads MBE weakness by topic", "audience": "law graduates studying", "page_type": "performance analytics dashboard"},
    {"id": "185", "category": "education", "brand": "Stargazer U", "goal": "help amateurs plan constellation observing nights", "audience": "amateur astronomers", "page_type": "observing planner with sky map"},
    {"id": "186", "category": "education", "brand": "Sew Simple", "goal": "match sewing beginners to patterns by difficulty", "audience": "beginner sewists", "page_type": "pattern matcher with video"},
    {"id": "187", "category": "education", "brand": "First Aid Fast", "goal": "refresh CPR skills in 10-minute micro-lessons", "audience": "workplace first-aiders", "page_type": "micro-course player with quiz"},
    {"id": "188", "category": "education", "brand": "Poetry Press", "goal": "help poets get structured workshop feedback", "audience": "emerging poets", "page_type": "workshop feedback thread"},
    {"id": "189", "category": "education", "brand": "Excelerate", "goal": "assess spreadsheet skills with a live sheet test", "audience": "job seekers proving Excel", "page_type": "skill assessment with sheet"},
    {"id": "190", "category": "education", "brand": "Field Trip", "goal": "let teachers collect permission slips digitally", "audience": "teachers and parents", "page_type": "permission slip flow"},
    {"id": "191", "category": "finance", "brand": "Rent Reward", "goal": "help renters build credit by reporting rent payments", "audience": "renters building credit", "page_type": "rent credit dashboard"},
    {"id": "192", "category": "finance", "brand": "Side Hustle Tax", "goal": "help gig workers estimate quarterly tax with mileage", "audience": "gig workers filing quarterly", "page_type": "income estimator with mileage"},
    {"id": "193", "category": "finance", "brand": "Willwise", "goal": "guide adults through a simple will with guardianship", "audience": "adults aged 30-50 without wills", "page_type": "will-building wizard"},
    {"id": "194", "category": "finance", "brand": "Kidvest", "goal": "show parents how custodial investing compounds over time", "audience": "parents saving for kids", "page_type": "custodial simulator"},
    {"id": "195", "category": "finance", "brand": "Bill Slayer", "goal": "help users find and cancel forgotten subscriptions", "audience": "users with subscription overload", "page_type": "subscription audit list"},
    {"id": "196", "category": "finance", "brand": "Credit Climb", "goal": "show rebuilders progress to secured-card graduation", "audience": "credit rebuilders", "page_type": "graduation progress tracker"},
    {"id": "197", "category": "finance", "brand": "Tithing", "goal": "help donors allocate giving across causes visually", "audience": "regular charitable donors", "page_type": "giving allocation editor"},
    {"id": "198", "category": "finance", "brand": "Freelance Float", "goal": "help freelancers smooth irregular income into salary", "audience": "freelancers with lumpy income", "page_type": "income smoothing planner"},
    {"id": "199", "category": "finance", "brand": "Rate Radar", "goal": "alert homeowners when refi saves real money", "audience": "homeowners with 6percent-plus rates", "page_type": "refi alert dashboard"},
    {"id": "200", "category": "insurance", "brand": "Petcover", "goal": "help pet owners file claims with photo vet bills", "audience": "pet owners with insurance", "page_type": "claim timeline with upload"},
    {"id": "201", "category": "finance", "brand": "Travel Fund", "goal": "help friend groups save for a trip in one sinking fund", "audience": "friend groups planning travel", "page_type": "sinking fund tracker"},
    {"id": "202", "category": "finance", "brand": "Wage Gap", "goal": "help job seekers explore salary distributions transparently", "audience": "job seekers negotiating offers", "page_type": "salary distribution explorer"},
    {"id": "203", "category": "finance", "brand": "Microloan Circle", "goal": "help neighbors run a peer lending circle fairly", "audience": "community lenders", "page_type": "lending circle dashboard"},
    {"id": "204", "category": "finance", "brand": "Estate Map", "goal": "help seniors inventory assets for heirs securely", "audience": "seniors planning estates", "page_type": "asset inventory vault"},
    {"id": "205", "category": "finance", "brand": "Crypto Tax", "goal": "help DeFi users categorize transactions for tax", "audience": "DeFi users at tax time", "page_type": "transaction categorizer table"},
    {"id": "206", "category": "finance", "brand": "Allowance", "goal": "help families turn chores into cash lessons", "audience": "families with kids 6-12", "page_type": "chore reward board"},
    {"id": "207", "category": "finance", "brand": "Severance Calc", "goal": "help laid-off employees estimate package and next steps", "audience": "recently laid-off employees", "page_type": "package estimator with checklist"},
    {"id": "208", "category": "finance", "brand": "Tip Jar", "goal": "help servers track tips by shift and section", "audience": "servers and baristas", "page_type": "tip logging with shift map"},
    {"id": "209", "category": "insurance", "brand": "Flood Cover", "goal": "explain flood risk and quote coverage simply", "audience": "coastal homeowners", "page_type": "risk map with quote flow"},
    {"id": "210", "category": "finance", "brand": "Audit Armor", "goal": "help sole proprietors vault receipts for deductions", "audience": "sole proprietors at tax time", "page_type": "receipt vault search"},
    {"id": "211", "category": "travel", "brand": "Redeye", "goal": "help budget travelers book sleep pods on long layovers", "audience": "budget travelers with red-eyes", "page_type": "pod booking with terminal map"},
    {"id": "212", "category": "travel", "brand": "Ferry Finder", "goal": "help island hoppers book ferries with weather-aware timetables", "audience": "island-hopping travelers", "page_type": "timetable search with weather"},
    {"id": "213", "category": "travel", "brand": "Ski Swap", "goal": "let skiers pre-fit rental sizes to skip shop lines", "audience": "resort skiers renting gear", "page_type": "rental pre-fit flow"},
    {"id": "214", "category": "travel", "brand": "Camp Cook", "goal": "help campers plan meals with cooler-space calculator", "audience": "car campers cooking outdoors", "page_type": "meal planner with pack list"},
    {"id": "215", "category": "hospitality", "brand": "Quiet Stay", "goal": "help light sleepers find hotels by noise ratings", "audience": "light sleepers traveling", "page_type": "hotel search with decibel badges"},
    {"id": "216", "category": "travel", "brand": "Visa Vault", "goal": "help travelers check visa needs with document checklist", "audience": "international travelers", "page_type": "requirement checker with docs"},
    {"id": "217", "category": "travel", "brand": "Tour Tips", "goal": "help backpackers find walking tours and tip fairly", "audience": "budget backpackers", "page_type": "tour detail with tip flow"},
    {"id": "218", "category": "hospitality", "brand": "Dinner Rush", "goal": "show weekend diners live wait times and join waitlist", "audience": "weekend diners without reservations", "page_type": "waitlist tracker"},
    {"id": "219", "category": "hospitality", "brand": "Picnic Pack", "goal": "let urban families order picnic bundles with park pickup", "audience": "urban families picnicking", "page_type": "bundle builder with pickup map"},
    {"id": "220", "category": "sports", "brand": "Marathon Map", "goal": "help spectators track runners live and find cheer spots", "audience": "marathon spectators", "page_type": "live runner map"},
    {"id": "221", "category": "travel", "brand": "Dive Log", "goal": "show divers viz and current at dive sites", "audience": "scuba divers planning dives", "page_type": "condition board with ratings"},
    {"id": "222", "category": "travel", "brand": "Cabin Share", "goal": "help friends split cabin costs with date voting", "audience": "friend groups renting cabins", "page_type": "cost splitter with calendar"},
    {"id": "223", "category": "travel", "brand": "Bike Tour", "goal": "help cyclists plan self-guided routes with elevation truth", "audience": "touring cyclists", "page_type": "route planner with elevation"},
    {"id": "224", "category": "travel", "brand": "Airport Nap", "goal": "help layover travelers compare lounge day passes", "audience": "travelers with 4-plus-hour layovers", "page_type": "lounge comparison with amenities"},
    {"id": "225", "category": "hospitality", "brand": "Food Truck", "goal": "show street-food fans live truck locations", "audience": "street-food fans", "page_type": "live location map feed"},
    {"id": "226", "category": "events", "brand": "Wedding Walk", "goal": "help couples schedule venue walkthroughs without email chains", "audience": "engaged couples touring venues", "page_type": "venue tour scheduler"},
    {"id": "227", "category": "hospitality", "brand": "Hostel Hub", "goal": "let solo travelers pick hostel beds with floor-plan view", "audience": "solo budget travelers", "page_type": "bed picker with floor plan"},
    {"id": "228", "category": "hospitality", "brand": "Tea House", "goal": "let cultural travelers book tea ceremonies by style", "audience": "cultural travelers", "page_type": "reservation flow with ceremony picker"},
    {"id": "229", "category": "travel", "brand": "Stargaze Stay", "goal": "help astrophotographers find dark-sky stays", "audience": "astrophotographers traveling", "page_type": "dark-sky map search"},
    {"id": "230", "category": "travel", "brand": "River Run", "goal": "help paddlers check flow gauges before renting kayaks", "audience": "recreational paddlers", "page_type": "flow gauge dashboard with rental"},
    {"id": "231", "category": "civic", "brand": "Ballot Buddy", "goal": "explain local ballot measures in plain language", "audience": "voters confused by legalese", "page_type": "ballot explainer"},
    {"id": "232", "category": "civic", "brand": "Snow Clear", "goal": "let winter residents request sidewalk plowing on a map", "audience": "winter city residents", "page_type": "plow request map"},
    {"id": "233", "category": "public service", "brand": "Tool Library", "goal": "let residents borrow public tools with hold queue", "audience": "residents doing home repair", "page_type": "tool catalog with holds"},
    {"id": "234", "category": "nonprofit", "brand": "Blood Drive", "goal": "help donors find slots after eligibility quiz", "audience": "first-time blood donors", "page_type": "slot finder with quiz"},
    {"id": "235", "category": "nonprofit", "brand": "Park Adopt", "goal": "let volunteers adopt park blocks for cleanup", "audience": "neighborhood volunteers", "page_type": "adoption map with tasks"},
    {"id": "236", "category": "public service", "brand": "Shelter Bed", "goal": "show outreach workers live shelter bed availability", "audience": "outreach workers and unhoused neighbors", "page_type": "bed availability board"},
    {"id": "237", "category": "civic", "brand": "Jury Duty", "goal": "let summoned citizens check in or defer online", "audience": "summoned jurors", "page_type": "check-in portal with deferral"},
    {"id": "238", "category": "civic", "brand": "Compost Crew", "goal": "help households sign up for curbside compost", "audience": "households new to composting", "page_type": "signup flow with calendar"},
    {"id": "239", "category": "community", "brand": "Little Library", "goal": "map neighborhood book-share boxes with inventory", "audience": "book neighbors sharing titles", "page_type": "share-box map"},
    {"id": "240", "category": "nonprofit", "brand": "Senior Ride", "goal": "match seniors with volunteer drivers transparently", "audience": "seniors needing rides", "page_type": "ride scheduler with driver cards"},
    {"id": "241", "category": "civic", "brand": "River Watch", "goal": "let anglers report water quality with photos", "audience": "anglers and kayakers", "page_type": "quality report map"},
    {"id": "242", "category": "civic", "brand": "Tree Tenure", "goal": "let residents adopt street trees with care guides", "audience": "residents greening blocks", "page_type": "tree adoption map"},
    {"id": "243", "category": "nonprofit", "brand": "Grant Seed", "goal": "help artists apply for microgrants with budget table", "audience": "emerging artists seeking funds", "page_type": "microgrant stepper"},
    {"id": "244", "category": "nonprofit", "brand": "Food Rescue", "goal": "match restaurant surplus with volunteer pickups fast", "audience": "food-rescue volunteers", "page_type": "pickup board with windows"},
    {"id": "245", "category": "nonprofit", "brand": "Tutor Match", "goal": "match students with free volunteer tutors by subject", "audience": "students needing free help", "page_type": "matcher with subject filters"},
    {"id": "246", "category": "public service", "brand": "Disaster Kit", "goal": "help families build emergency kits by hazard", "audience": "families in hazard zones", "page_type": "kit builder with checklist"},
    {"id": "247", "category": "civic", "brand": "Noise Report", "goal": "help downtown residents file noise complaints with evidence", "audience": "downtown residents", "page_type": "complaint form with guide"},
    {"id": "248", "category": "civic", "brand": "Bike Lane", "goal": "let cyclists report blocked bike lanes with GPS photo", "audience": "bike commuters", "page_type": "obstruction reporter"},
    {"id": "249", "category": "public service", "brand": "Language Access", "goal": "help residents request interpreters in their language", "audience": "residents with limited English", "page_type": "request flow with picker"},
    {"id": "250", "category": "civic", "brand": "Poll Worker", "goal": "help volunteers sign up for poll shifts with training", "audience": "civic volunteers", "page_type": "shift signup with training"},
    {"id": "251", "category": "music", "brand": "Mixtape", "goal": "let friends build a collaborative mixtape in order", "audience": "friends making party mixes", "page_type": "mixtape builder with ordering"},
    {"id": "252", "category": "media", "brand": "Audiobook Club", "goal": "help book clubs listen together with shared notes", "audience": "audiobook clubs", "page_type": "listen scheduler with notes"},
    {"id": "253", "category": "media", "brand": "Set Design", "goal": "help indie filmmakers inventory props with tags", "audience": "indie art departments", "page_type": "prop inventory grid"},
    {"id": "254", "category": "media", "brand": "Photo Walk", "goal": "guide photographers on routes with creative challenges", "audience": "hobby photographers", "page_type": "route cards with challenges"},
    {"id": "255", "category": "media", "brand": "Zine Maker", "goal": "let zinesters lay out printable 8-page zines", "audience": "zine makers", "page_type": "zine page editor"},
    {"id": "256", "category": "video", "brand": "Subtitle Sync", "goal": "help editors fix subtitle timing with waveform", "audience": "video editors fixing subs", "page_type": "timing editor with waveform"},
    {"id": "257", "category": "media", "brand": "Radio Archive", "goal": "help listeners browse college radio archives by decade", "audience": "college radio fans", "page_type": "archive search with filters"},
    {"id": "258", "category": "music", "brand": "Lyric Lab", "goal": "help songwriters find rhymes with syllable counts", "audience": "songwriters stuck on verses", "page_type": "lyric editor with rhyme panel"},
    {"id": "259", "category": "culture", "brand": "Museum Late", "goal": "promote after-hours museum nights to young members", "audience": "museum members 21-35", "page_type": "event program with RSVP"},
    {"id": "260", "category": "media", "brand": "Film Club", "goal": "let film fans discuss without spoiler accidents", "audience": "film fans avoiding spoilers", "page_type": "discussion threads with blur"},
    {"id": "261", "category": "music", "brand": "Busk", "goal": "help fans find buskers live and tip digitally", "audience": "street-music fans", "page_type": "performer map with tip button"},
    {"id": "262", "category": "media", "brand": "Comic Panel", "goal": "let readers binge webcomics with progress memory", "audience": "webcomic readers", "page_type": "episode reader with progress"},
    {"id": "263", "category": "music", "brand": "Remix Rights", "goal": "help producers check sample clearance risk early", "audience": "bedroom producers sampling", "page_type": "clearance checker"},
    {"id": "264", "category": "culture", "brand": "Dance Class", "goal": "help dancers find drop-in classes by true level", "audience": "adult dance beginners", "page_type": "class finder with level tags"},
    {"id": "265", "category": "community", "brand": "Book Swap", "goal": "help neighbors swap books on a building shelf", "audience": "apartment neighbors", "page_type": "swap shelf inventory"},
    {"id": "266", "category": "events", "brand": "Trivia Night", "goal": "let trivia teams sign up and vote categories", "audience": "bar trivia teams", "page_type": "team signup with vote"},
    {"id": "267", "category": "music", "brand": "Vinyl Press", "goal": "help indie labels price small vinyl runs", "audience": "indie labels pressing 300 copies", "page_type": "cost calculator with timeline"},
    {"id": "268", "category": "events", "brand": "Docu Fest", "goal": "let festival goers ballot documentary screenings", "audience": "documentary festival goers", "page_type": "screening ballot with ratings"},
    {"id": "269", "category": "wellness", "brand": "Lullaby", "goal": "help parents mix white noise for baby sleep", "audience": "parents of newborns", "page_type": "sound mixer with timer"},
    {"id": "270", "category": "events", "brand": "Stage Door", "goal": "help theater fans enter standby lotteries fairly", "audience": "budget theater fans", "page_type": "lotto entry with alerts"},
    {"id": "271", "category": "community", "brand": "Dog Park", "goal": "show dog owners off-leash hours and etiquette", "audience": "urban dog owners", "page_type": "park detail with hours"},
    {"id": "272", "category": "community", "brand": "Nanny Share", "goal": "help two families coordinate a nanny share schedule", "audience": "families sharing a nanny", "page_type": "share calendar with split"},
    {"id": "273", "category": "community", "brand": "Sober Social", "goal": "help sober folks find alcohol-free nights out", "audience": "sober community members", "page_type": "event finder with vibe tags"},
    {"id": "274", "category": "community", "brand": "Repair Cafe", "goal": "let residents book fix-it slots with item details", "audience": "residents repairing goods", "page_type": "repair booking with picker"},
    {"id": "275", "category": "sports", "brand": "Climb Gym", "goal": "help climbers track boulder problems by grade", "audience": "indoor boulderers", "page_type": "problem tracker with filters"},
    {"id": "276", "category": "community", "brand": "Board Game", "goal": "match game-night groups by library and weight", "audience": "board gamers seeking groups", "page_type": "night matcher with library"},
    {"id": "277", "category": "job board", "brand": "Internship Alley", "goal": "surface only paid internships with pay filters", "audience": "students seeking paid roles", "page_type": "internship board with pay filter"},
    {"id": "278", "category": "job board", "brand": "Shift Swap", "goal": "let retail workers swap shifts with manager approval", "audience": "retail shift workers", "page_type": "swap board with approval"},
    {"id": "279", "category": "productivity", "brand": "Salary Review", "goal": "help employees prep reviews with wins log", "audience": "employees before reviews", "page_type": "review prep worksheet"},
    {"id": "280", "category": "community", "brand": "Roommate", "goal": "generate fair chore rotations with reminders", "audience": "roommates splitting chores", "page_type": "chore wheel with reminders"},
    {"id": "281", "category": "real estate", "brand": "Storage Share", "goal": "let neighbors rent garage corners with dimensions", "audience": "neighbors needing storage", "page_type": "space listings with dimensions"},
    {"id": "282", "category": "community", "brand": "Carpool School", "goal": "organize school pickup carpools with seat info", "audience": "parents doing pickup", "page_type": "carpool map with seats"},
    {"id": "283", "category": "education", "brand": "Mentor Mesh", "goal": "let early-career folks book 30-min mentor chats", "audience": "early-career professionals", "page_type": "mentor cards with slots"},
    {"id": "284", "category": "travel", "brand": "Freelance Visa", "goal": "guide freelancers through digital-nomad visa paperwork", "audience": "freelancers moving abroad", "page_type": "checklist tracker with vault"},
    {"id": "285", "category": "real estate", "brand": "Tiny Home", "goal": "help tiny-home owners find parking with hookups", "audience": "tiny-home owners", "page_type": "parking map with filters"},
    {"id": "286", "category": "community", "brand": "Beekeeper", "goal": "help beekeepers log hive inspections with photos", "audience": "backyard beekeepers", "page_type": "inspection timeline with photo"},
    {"id": "287", "category": "community", "brand": "Coral Club", "goal": "help aquarists log reef parameters with alerts", "audience": "reef tank owners", "page_type": "parameter charts with alerts"},
    {"id": "288", "category": "community", "brand": "Forage", "goal": "show urban foragers safe spots with safety notes", "audience": "urban foragers", "page_type": "foraging map with notes"},
    {"id": "289", "category": "community", "brand": "Death Doula", "goal": "help families organize end-of-life wishes gently", "audience": "families planning ahead", "page_type": "plan organizer with prompts"},
    {"id": "290", "category": "dating", "brand": "Baby Name", "goal": "help couples find a name both veto-approve", "audience": "expecting couples disagreeing", "page_type": "name swipe matcher"},
    {"id": "291", "category": "marketplace", "brand": "Garage Sale", "goal": "map multi-house garage sales with item tags", "audience": "bargain hunters driving routes", "page_type": "sale map with tags"},
    {"id": "292", "category": "community", "brand": "Skill Swap", "goal": "let neighbors trade hours of skills fairly", "audience": "neighbors exchanging help", "page_type": "swap board with ledger"},
    {"id": "293", "category": "community", "brand": "Co-op Cart", "goal": "help food co-op members pick shifts and trade", "audience": "food co-op members", "page_type": "shift calendar with trade"},
    {"id": "294", "category": "logistics", "brand": "Ferry Commute", "goal": "help commuters manage ferry passes with delay alerts", "audience": "ferry commuters", "page_type": "pass manager with alerts"},
    {"id": "295", "category": "community", "brand": "Gallery Sit", "goal": "let artists trade gallery-sitting hours", "audience": "emerging artists", "page_type": "sitter calendar with portfolio"},
    {"id": "296", "category": "travel", "brand": "Trail Angels", "goal": "help thru-hikers plan resupply by mile marker", "audience": "thru-hikers on long trails", "page_type": "resupply planner with miles"},
    {"id": "297", "category": "accessibility", "brand": "Low Vision Cook", "goal": "let low-vision cooks follow recipes hands-free with voice", "audience": "low-vision home cooks", "page_type": "step player with voice"},
    {"id": "298", "category": "accessibility", "brand": "Deaf Events", "goal": "surface events with ASL interpretation clearly", "audience": "Deaf community members", "page_type": "event finder with badges"},
    {"id": "299", "category": "nonprofit", "brand": "Refugee Welcome", "goal": "help sponsors track resettlement tasks for families", "audience": "community sponsors", "page_type": "task tracker with needs"},
    {"id": "300", "category": "community", "brand": "Time Bank", "goal": "let members bank hours helping neighbors", "audience": "time-bank members", "page_type": "hour ledger with requests"},
]

NEW_PALETTES = [
    {"name": "desert dusk", "bg": "#FBF3E4", "surface": "#FFFFFF", "text": "#2B2118", "muted": "#8A7663", "accent": "#C17A3D", "focus": "#0B5FFF"},
    {"name": "ocean deep", "bg": "#0E1A24", "surface": "#16293A", "text": "#F2F5F7", "muted": "#93A5B5", "accent": "#4CC3D9", "focus": "#7CFFB2"},
    {"name": "forest mist", "bg": "#EDF3EC", "surface": "#FFFFFF", "text": "#1C2A21", "muted": "#5F7267", "accent": "#2F7D4F", "focus": "#003DFF"},
    {"name": "lavender field", "bg": "#F6F1FB", "surface": "#FFFFFF", "text": "#2A1E3F", "muted": "#72648C", "accent": "#7C4DFF", "focus": "#0050FF"},
    {"name": "terracotta sun", "bg": "#FFF4E8", "surface": "#FFFFFF", "text": "#3A2015", "muted": "#8A6A58", "accent": "#E05B25", "focus": "#0022FF"},
    {"name": "slate tech", "bg": "#F1F4F8", "surface": "#FFFFFF", "text": "#16202E", "muted": "#5D6E84", "accent": "#0EA5A0", "focus": "#4F00FF"},
    {"name": "berry noir", "bg": "#17111A", "surface": "#221722", "text": "#F9F0F5", "muted": "#A894A5", "accent": "#FF5C8A", "focus": "#5CFFD1"},
    {"name": "moss stone", "bg": "#F2F1EB", "surface": "#FFFFFF", "text": "#23281F", "muted": "#6A7260", "accent": "#6B8E4E", "focus": "#1A3DFF"},
    {"name": "arctic paper", "bg": "#F7FAFC", "surface": "#FFFFFF", "text": "#1A2A3A", "muted": "#5F7386", "accent": "#2B7FFF", "focus": "#FF4400"},
    {"name": "golden hour", "bg": "#FFFBEB", "surface": "#FFFFFF", "text": "#3B2E12", "muted": "#8A7A55", "accent": "#B8860B", "focus": "#0022DD"},
    {"name": "eucalyptus", "bg": "#EAF2EE", "surface": "#FFFFFF", "text": "#1E2E28", "muted": "#5E7A6E", "accent": "#1F9D6B", "focus": "#2B00FF"},
    {"name": "clay cream", "bg": "#FAF6F0", "surface": "#FFFFFF", "text": "#2E2A26", "muted": "#7D746B", "accent": "#A85B2A", "focus": "#0033FF"},
    {"name": "midnight civic", "bg": "#0F172A", "surface": "#1A2540", "text": "#F1F5F9", "muted": "#8B98B0", "accent": "#FBBF24", "focus": "#38FFB2"},
    {"name": "coral reef", "bg": "#FFF5F2", "surface": "#FFFFFF", "text": "#2B1B18", "muted": "#8A655F", "accent": "#E14D3A", "focus": "#003DFF"},
    {"name": "pine night", "bg": "#101C18", "surface": "#182825", "text": "#EAF4EE", "muted": "#8AA699", "accent": "#4ADE80", "focus": "#8AB4FF"},
    {"name": "sandstone", "bg": "#F5EFE6", "surface": "#FFFFFF", "text": "#2D2A26", "muted": "#7A7167", "accent": "#8C6A3C", "focus": "#1A40FF"},
    {"name": "iris dusk", "bg": "#EFEAFF", "surface": "#FFFFFF", "text": "#221D3A", "muted": "#6A628A", "accent": "#6C4CF1", "focus": "#0055FF"},
    {"name": "copper lab", "bg": "#F8F5F2", "surface": "#FFFFFF", "text": "#211D1A", "muted": "#6E655E", "accent": "#B45309", "focus": "#0022EE"},
    {"name": "kelp fog", "bg": "#EEF2F0", "surface": "#FFFFFF", "text": "#1F2A2E", "muted": "#5D7278", "accent": "#0E7490", "focus": "#3B00FF"},
    {"name": "plum paper", "bg": "#FAF2F6", "surface": "#FFFFFF", "text": "#33182A", "muted": "#8A647E", "accent": "#C13A7A", "focus": "#0022CC"},
]

NEW_TYPOS = [
    {"name": "grotesk-editorial", "heading": "'Space Grotesk','Segoe UI',sans-serif", "body": "Inter,'Segoe UI',sans-serif", "mono": "'JetBrains Mono',Consolas,monospace", "scale": "1.333 perfect-fourth"},
    {"name": "fraunces-inter", "heading": "Fraunces,Georgia,serif", "body": "Inter,Arial,sans-serif", "mono": "'IBM Plex Mono',monospace", "scale": "1.414 augmented-fourth"},
    {"name": "sora-system", "heading": "Sora,'Trebuchet MS',sans-serif", "body": "'Atkinson Hyperlegible',Arial,sans-serif", "mono": "ui-monospace,Consolas,monospace", "scale": "1.25 major-third"},
    {"name": "libre-baskerville", "heading": "'Libre Baskerville',Georgia,serif", "body": "'Source Sans 3',Arial,sans-serif", "mono": "'Source Code Pro',monospace", "scale": "1.5 perfect-fifth"},
    {"name": "dm-sans-mono", "heading": "'DM Sans',Verdana,sans-serif", "body": "'DM Sans',Verdana,sans-serif", "mono": "'DM Mono',monospace", "scale": "1.2 minor-third"},
    {"name": "outfit-merriweather", "heading": "Outfit,'Arial Black',sans-serif", "body": "Merriweather,Georgia,serif", "mono": "'Courier New',monospace", "scale": "1.333 perfect-fourth"},
    {"name": "manrope-newsreader", "heading": "Manrope,Arial,sans-serif", "body": "Newsreader,Georgia,serif", "mono": "'Noto Sans Mono',monospace", "scale": "1.25 major-third"},
    {"name": "lexend-readable", "heading": "Lexend,Verdana,sans-serif", "body": "Lexend,Verdana,sans-serif", "mono": "'Roboto Mono',monospace", "scale": "1.125 major-second"},
    {"name": "zodiak-inter", "heading": "Zodiak,'Palatino Linotype',serif", "body": "Inter,'Helvetica Neue',sans-serif", "mono": "'Fira Code',monospace", "scale": "1.618 golden-ratio"},
    {"name": "public-sans", "heading": "'Public Sans','Segoe UI',sans-serif", "body": "'Public Sans','Segoe UI',sans-serif", "mono": "'SFMono-Regular',Consolas,monospace", "scale": "1.2 minor-third"},
]


def build_more_record(seq_num: int, prod: dict, palette: dict, typo: dict, archetype_fn, nav: str, interaction: str, responsive: str, radius: str, space: str) -> dict:
    example_id = f"{NAMESPACE}_design_{seq_num:03d}"
    initial_code, critic_feedback, corrected_code = archetype_fn(palette, prod, typo, radius, space, nav, interaction, responsive)
    task = (f"Design a {prod['page_type']} for {prod['brand']}, a {prod['category']} product. "
            f"The primary goal is to {prod['goal']}. Target audience: {prod['audience']}.")
    constraints = [
        "Must work at both 1440x900 desktop and 390x844 mobile viewports.",
        "Include visible keyboard focus states and screen reader landmarks.",
        f"Content must be specific to {prod['audience']} - no generic placeholder text.",
        f"Navigation should use a {nav.lower()} pattern.",
    ]
    design_spec = {
        "information_architecture": f"A {prod['page_type']} structured for {prod['audience']}. Navigation uses {nav.lower()}. Content prioritizes {prod['goal']}.",
        "layout": f"{archetype_fn.__name__.replace('gen_','').replace('_',' ').title()} composition with {palette['name']} visual direction. Responsive strategy: {responsive}.",
        "tokens": {"background": palette["bg"], "surface": palette["surface"], "text": palette["text"], "muted": palette["muted"], "accent": palette["accent"], "focus": palette["focus"], "radius": radius, "space": space},
        "typography": f"Heading: {typo['heading']}. Body: {typo['body']}. Monospace: {typo['mono']}. Scale: {typo['scale']}.",
        "components": _components_for_archetype(archetype_fn.__name__),
        "responsive_rules": [responsive],
        "interaction_states": [interaction],
        "accessibility": "Semantic landmarks (header, nav, main, footer), one h1, visible focus styles, ARIA attributes on interactive widgets, no color-only meaning, keyboard-navigable controls.",
    }
    return {"example_id": example_id, "task": task, "constraints": constraints, "reference_screenshots": [],
        "research_evidence": [f"Users in the {prod['category']} domain expect clear calls to action and minimal friction.", f"Research shows {prod['audience']} prefer interfaces that surface the most relevant information first."],
        "design_spec": design_spec, "initial_code": initial_code,
        "render_report": {"status": "not_rendered",
            "viewports": [{"width": 1440, "height": 900, "initial": _null_viewport(), "corrected": _null_viewport()}, {"width": 390, "height": 844, "initial": _null_viewport(), "corrected": _null_viewport()}],
            "visual_score": None, "accessibility_score": None, "screenshots_captured": False},
        "critic_feedback": critic_feedback, "corrected_code": corrected_code, "quality_score": None, "status": "needs_review", "source": f"agent-{NAMESPACE}"}


def generate_more() -> list[dict]:
    records = []
    n_arch = len(ARCHETYPE_GENERATORS)
    for i, prod in enumerate(NEW_PRODUCTS):
        seq = 101 + i
        arch = ARCHETYPE_GENERATORS[(i + 7) % n_arch]
        pal = NEW_PALETTES[i % len(NEW_PALETTES)]
        typo = NEW_TYPOS[(i + 3) % len(NEW_TYPOS)]
        nav = NAV_PATTERNS[(i + 5) % len(NAV_PATTERNS)]
        inter = INTERACTION_MODELS[(i + 4) % len(INTERACTION_MODELS)]
        resp = RESPONSIVE_STRATEGIES[(i + 6) % len(RESPONSIVE_STRATEGIES)]
        rad = RADIUS_LANGUAGE[(i + 2) % len(RADIUS_LANGUAGE)]
        sp = SPACING_RHYTHMS[(i + 8) % len(SPACING_RHYTHMS)]
        records.append(build_more_record(seq, prod, pal, typo, arch, nav, inter, resp, rad, sp))
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="outputs/forma_single_101_300.jsonl")
    args = ap.parse_args()
    recs = generate_more()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"output": str(out), "records_generated": len(recs), "ids": f"{recs[0]['example_id']}..{recs[-1]['example_id']}", "unique_ids": len(set(r['example_id'] for r in recs))}, indent=2))

if __name__ == "__main__":
    main()
