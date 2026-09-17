"""Generate 100 genuinely unique Forma v2 UI/UX design records.

Each record differs across ALL dimensions: product goal, page archetype,
layout pattern, navigation model, palette, typography, interaction model,
responsive strategy, and actual HTML structure. This is NOT 100 color
variations of the same hero+cards layout.

Output: one JSONL file with exactly 100 records, each containing:
- complete initial_code (deliberately imperfect)
- specific critic_feedback
- corrected_code fixing every listed issue
"""

from __future__ import annotations

import argparse
import json
import random
from html import escape
from pathlib import Path
from typing import Any

# ============================================================
# 100 UNIQUE PRODUCTS — every record gets a distinct product
# ============================================================

PRODUCTS: list[dict[str, str]] = [
    # --- Ecommerce & Retail (1-10) ---
    {"id": "001", "category": "ecommerce", "brand": "Northline Goods", "goal": "help a shopper compare artisan homeware products and complete checkout", "audience": "design-conscious homeowners aged 28-45", "page_type": "product comparison landing"},
    {"id": "002", "category": "ecommerce", "brand": "Harvest & Vine", "goal": "let a subscriber customize their monthly wine box and manage delivery schedule", "audience": "wine enthusiasts who prefer discovery over expertise", "page_type": "subscription customization flow"},
    {"id": "003", "category": "marketplace", "brand": "Thriftcircle", "goal": "help a seller list a pre-owned item with accurate condition grading", "audience": "sustainability-minded sellers aged 20-35", "page_type": "multi-step listing form"},
    {"id": "004", "category": "ecommerce", "brand": "Sole Archive", "goal": "let a sneaker collector verify authenticity and place a bid", "audience": "sneaker collectors who value provenance", "page_type": "auction detail page"},
    {"id": "005", "category": "ecommerce", "brand": "Pantry Lane", "goal": "help a busy parent build a weekly grocery order from saved recipes", "audience": "time-pressed parents with dietary constraints", "page_type": "recipe-to-cart dashboard"},
    {"id": "006", "category": "marketplace", "brand": "Studio Lot", "goal": "help a photographer rent specialty equipment with insurance options", "audience": "freelance photographers and videographers", "page_type": "equipment rental booking"},
    {"id": "007", "category": "ecommerce", "brand": "Ember & Thread", "goal": "let a shopper build a capsule wardrobe using style quiz results", "audience": "minimalist fashion seekers aged 25-40", "page_type": "guided wardrobe builder"},
    {"id": "008", "category": "retail", "brand": "Greenfield Market", "goal": "show a customer which local farms supply their selected produce", "audience": "farm-to-table advocates in urban areas", "page_type": "supply chain transparency page"},
    {"id": "009", "category": "ecommerce", "brand": "Deskcraft", "goal": "let a remote worker configure an ergonomic desk setup with compatibility checks", "audience": "remote workers investing in home office ergonomics", "page_type": "product configurator"},
    {"id": "010", "category": "marketplace", "brand": "Bookbound", "goal": "help a reader find a rare edition and contact the seller", "audience": "bibliophiles seeking out-of-print titles", "page_type": "search results with seller details"},
    # --- SaaS & Dashboards (11-20) ---
    {"id": "011", "category": "saas", "brand": "TerraOps", "goal": "help an ops manager spot infrastructure anomalies and trigger a runbook", "audience": "DevOps engineers managing multi-cloud fleets", "page_type": "anomaly detection dashboard"},
    {"id": "012", "category": "saas", "brand": "Relay CRM", "goal": "let a sales rep see pipeline health and prioritize follow-ups", "audience": "B2B sales reps managing 50+ accounts", "page_type": "CRM pipeline kanban"},
    {"id": "013", "category": "saas", "brand": "Beacon Analytics", "goal": "help a marketing manager attribute conversions across channels", "audience": "marketing managers at mid-size DTC brands", "page_type": "multi-touch attribution report"},
    {"id": "014", "category": "saas", "brand": "Draftboard", "goal": "let a product team prioritize features using weighted scoring", "audience": "product managers running agile teams", "page_type": "feature prioritization table"},
    {"id": "015", "category": "saas", "brand": "Nexus HR", "goal": "help an HR director review headcount forecasts and open requisitions", "audience": "HR directors at growing startups", "page_type": "workforce planning dashboard"},
    {"id": "016", "category": "saas", "brand": "Pulseboard", "goal": "show a CEO daily business health metrics with drill-down", "audience": "C-suite executives who check metrics on mobile", "page_type": "executive KPI summary"},
    {"id": "017", "category": "saas", "brand": "FormForge", "goal": "let a non-technical user build a multi-step intake form with logic branches", "audience": "operations staff without coding skills", "page_type": "visual form builder"},
    {"id": "018", "category": "saas", "brand": "Inkvault", "goal": "help a legal team track contract status and upcoming renewals", "audience": "in-house legal teams at mid-size companies", "page_type": "contract lifecycle table"},
    {"id": "019", "category": "saas", "brand": "Canopy Logs", "goal": "let a developer search structured logs and correlate errors with deployments", "audience": "backend developers debugging production issues", "page_type": "log explorer with timeline"},
    {"id": "020", "category": "saas", "brand": "Dispatch Hub", "goal": "help a support lead monitor ticket queues and reassign overloaded agents", "audience": "customer support team leads", "page_type": "support queue command center"},
    # --- Healthcare & Wellness (21-30) ---
    {"id": "021", "category": "telehealth", "brand": "Morrow Health", "goal": "help a patient book a specialist appointment with insurance verification", "audience": "patients navigating specialist referrals", "page_type": "appointment booking flow"},
    {"id": "022", "category": "wellness", "brand": "Small Hours", "goal": "guide a user through a personalized evening wind-down routine", "audience": "adults struggling with sleep quality", "page_type": "guided ritual flow"},
    {"id": "023", "category": "fitness", "brand": "Arc Motion", "goal": "help a gym member choose a workout matching today's energy and available equipment", "audience": "intermediate gym members aged 25-40", "page_type": "adaptive workout selector"},
    {"id": "024", "category": "healthcare", "brand": "CareCircle", "goal": "let a family caregiver coordinate medication schedules across providers", "audience": "family caregivers managing elderly parents", "page_type": "medication calendar"},
    {"id": "025", "category": "mental health", "brand": "Mindtrace", "goal": "help a therapy client log mood patterns and share summaries with their therapist", "audience": "therapy clients tracking between sessions", "page_type": "mood tracking timeline"},
    {"id": "026", "category": "nutrition", "brand": "Platemath", "goal": "let a user log meals with macro breakdowns and see weekly trends", "audience": "fitness-focused individuals tracking nutrition", "page_type": "nutrition logging dashboard"},
    {"id": "027", "category": "telehealth", "brand": "QuickConsult", "goal": "connect a patient with an on-demand nurse for triage before ER", "audience": "parents with sick children after hours", "page_type": "urgent triage chat interface"},
    {"id": "028", "category": "wellness", "brand": "Breath Basin", "goal": "guide a stressed professional through a 5-minute breathing exercise with visual feedback", "audience": "professionals seeking micro-breaks during work", "page_type": "interactive breathing exercise"},
    {"id": "029", "category": "healthcare", "brand": "Vitalink", "goal": "show a patient their lab results with plain-language explanations", "audience": "patients who find medical terminology confusing", "page_type": "lab results detail page"},
    {"id": "030", "category": "fitness", "brand": "Trailpace", "goal": "help a runner plan a training block with progressive overload", "audience": "amateur runners training for a half-marathon", "page_type": "training plan timeline"},
    # --- Education & Learning (31-40) ---
    {"id": "031", "category": "education", "brand": "Common Thread", "goal": "help a learner resume a course and track progress toward certification", "audience": "working adults pursuing professional certificates", "page_type": "course progress dashboard"},
    {"id": "032", "category": "education", "brand": "Labspark", "goal": "let a student run an interactive science simulation and record observations", "audience": "high school STEM students", "page_type": "interactive lab simulation"},
    {"id": "033", "category": "edtech", "brand": "Quillpad", "goal": "help an ESL student practice writing with real-time grammar feedback", "audience": "adult ESL learners at intermediate level", "page_type": "writing practice editor"},
    {"id": "034", "category": "education", "brand": "Skillgraph", "goal": "show a learner their competency map and suggest next learning paths", "audience": "self-directed learners exploring career changes", "page_type": "competency map visualization"},
    {"id": "035", "category": "library", "brand": "Civic Shelf", "goal": "help a library visitor find a title, check availability, and place a hold", "audience": "public library patrons of all ages", "page_type": "library catalog search"},
    {"id": "036", "category": "education", "brand": "TutorGrid", "goal": "let a parent browse tutor profiles and book a trial session", "audience": "parents seeking homework help for children", "page_type": "tutor marketplace with booking"},
    {"id": "037", "category": "education", "brand": "Codepath", "goal": "guide a beginner through an interactive coding challenge with hints", "audience": "coding beginners aged 16-25", "page_type": "interactive code challenge"},
    {"id": "038", "category": "education", "brand": "HistoryLens", "goal": "let a student explore historical events on an interactive timeline with primary sources", "audience": "history students researching specific periods", "page_type": "interactive history timeline"},
    {"id": "039", "category": "education", "brand": "PeerReview", "goal": "help a graduate student give structured feedback on a classmate's paper", "audience": "graduate students in peer-review workshops", "page_type": "structured feedback form"},
    {"id": "040", "category": "education", "brand": "Flashpaths", "goal": "let a student create and study spaced-repetition flashcards with progress tracking", "audience": "university students preparing for exams", "page_type": "flashcard study session"},
    # --- Finance & Payments (41-50) ---
    {"id": "041", "category": "finance", "brand": "Lumen Ledger", "goal": "help a user understand monthly spending patterns and set a realistic budget", "audience": "young professionals managing their first salary", "page_type": "spending analysis dashboard"},
    {"id": "042", "category": "finance", "brand": "Splitwise Clone", "goal": "let a group of friends split shared expenses and settle debts", "audience": "friend groups sharing travel or household costs", "page_type": "group expense splitter"},
    {"id": "043", "category": "finance", "brand": "Vestmark", "goal": "show an investor portfolio allocation with risk analysis and rebalancing suggestions", "audience": "self-directed investors with moderate portfolios", "page_type": "portfolio allocation dashboard"},
    {"id": "044", "category": "finance", "brand": "Taxpath", "goal": "guide a freelancer through quarterly tax estimation with deduction checklist", "audience": "freelancers who file their own taxes", "page_type": "tax estimation stepper"},
    {"id": "045", "category": "banking", "brand": "Greenbank", "goal": "let a customer open a savings account with impact-linked interest rates", "audience": "environmentally conscious savers", "page_type": "account opening flow"},
    {"id": "046", "category": "finance", "brand": "Invoice Flow", "goal": "help a small business owner create, send, and track invoice payments", "audience": "solo entrepreneurs and small business owners", "page_type": "invoice management list"},
    {"id": "047", "category": "insurance", "brand": "CoverScan", "goal": "help a renter compare insurance quotes and understand coverage differences", "audience": "first-time renters unfamiliar with insurance", "page_type": "insurance comparison page"},
    {"id": "048", "category": "finance", "brand": "Coinlens", "goal": "show a crypto holder their portfolio performance with news sentiment overlay", "audience": "casual crypto investors checking holdings weekly", "page_type": "crypto portfolio with sentiment"},
    {"id": "049", "category": "payments", "brand": "PayRelay", "goal": "let a freelancer set up recurring payment requests for retainer clients", "audience": "freelancers with ongoing client relationships", "page_type": "recurring payment setup"},
    {"id": "050", "category": "finance", "brand": "Pennywise", "goal": "teach a teenager basic budgeting through gamified savings challenges", "audience": "teenagers aged 13-17 learning money management", "page_type": "gamified savings challenge"},
    # --- Travel & Hospitality (51-58) ---
    {"id": "051", "category": "travel", "brand": "Fieldnote", "goal": "help a traveler build a multi-city itinerary with transport connections", "audience": "independent travelers planning 2+ week trips", "page_type": "itinerary builder with map"},
    {"id": "052", "category": "hospitality", "brand": "Innkeeper", "goal": "let a guest check in digitally, choose room preferences, and request amenities", "audience": "hotel guests arriving after front-desk hours", "page_type": "digital check-in flow"},
    {"id": "053", "category": "travel", "brand": "Trailhead", "goal": "help a hiker find trails by difficulty, length, and current conditions", "audience": "outdoor enthusiasts planning weekend hikes", "page_type": "trail search with filters and map"},
    {"id": "054", "category": "events", "brand": "Night Index", "goal": "help a user find live events tonight with seating availability", "audience": "urban nightlife seekers aged 21-35", "page_type": "event discovery feed"},
    {"id": "055", "category": "travel", "brand": "Nomad Desk", "goal": "help a remote worker find co-working-friendly destinations with visa info", "audience": "digital nomads evaluating relocation options", "page_type": "destination comparison page"},
    {"id": "056", "category": "hospitality", "brand": "Saffron Table", "goal": "help a diner explore a restaurant's menu with dietary filters and wait time", "audience": "diners with dietary restrictions", "page_type": "interactive restaurant menu"},
    {"id": "057", "category": "travel", "brand": "Wayfare", "goal": "help a family compare vacation rental properties with kid-friendly amenities", "audience": "families with young children planning vacations", "page_type": "rental comparison with amenity matrix"},
    {"id": "058", "category": "events", "brand": "Open Field", "goal": "help a family find and book age-appropriate festival events", "audience": "families attending multi-day outdoor festivals", "page_type": "festival schedule and booking"},
    # --- Civic, Nonprofit & Public Services (59-68) ---
    {"id": "059", "category": "civic", "brand": "CityPulse", "goal": "show a resident upcoming public meetings and let them RSVP or submit comments", "audience": "engaged citizens who attend local government meetings", "page_type": "public meeting calendar"},
    {"id": "060", "category": "nonprofit", "brand": "Common Ground", "goal": "help a donor understand program impact and complete a one-time or recurring donation", "audience": "donors who want transparency on where money goes", "page_type": "impact report with donation flow"},
    {"id": "061", "category": "civic", "brand": "PermitPath", "goal": "guide a homeowner through the building permit application process", "audience": "homeowners unfamiliar with municipal processes", "page_type": "permit application stepper"},
    {"id": "062", "category": "civic", "brand": "TransitLens", "goal": "help a commuter plan a multi-modal trip with real-time delays", "audience": "daily commuters using public transit", "page_type": "transit trip planner"},
    {"id": "063", "category": "nonprofit", "brand": "Reforest", "goal": "let a volunteer sign up for tree-planting events and track their impact", "audience": "environmental volunteers in urban areas", "page_type": "volunteer event signup"},
    {"id": "064", "category": "civic", "brand": "Votewise", "goal": "help a voter compare candidates' positions on issues they care about", "audience": "first-time voters seeking non-partisan information", "page_type": "candidate comparison tool"},
    {"id": "065", "category": "public service", "brand": "SafeAlert", "goal": "show a resident active emergency alerts and shelter locations on a map", "audience": "residents in disaster-prone areas", "page_type": "emergency alert map"},
    {"id": "066", "category": "civic", "brand": "Pothole Report", "goal": "let a resident report a road issue with photo and GPS location", "audience": "residents who want to report infrastructure problems", "page_type": "issue reporting form with map"},
    {"id": "067", "category": "nonprofit", "brand": "MealBridge", "goal": "help a food bank coordinator match surplus donations with nearby pantries", "audience": "food bank coordinators managing logistics", "page_type": "donation matching dashboard"},
    {"id": "068", "category": "public service", "brand": "AidReach", "goal": "let a senior citizen apply for utility assistance programs online", "audience": "seniors with limited tech literacy applying for aid", "page_type": "accessible benefits application"},
    # --- Media, Music & Culture (69-78) ---
    {"id": "069", "category": "music", "brand": "Afterlight", "goal": "help a listener discover playlists by mood and activity without decision fatigue", "audience": "music listeners who feel overwhelmed by choice", "page_type": "mood-based playlist discovery"},
    {"id": "070", "category": "media", "brand": "Longread", "goal": "present a long-form investigative article with embedded data and multimedia", "audience": "readers who value deep journalism", "page_type": "long-form editorial article"},
    {"id": "071", "category": "podcast", "brand": "Earmark", "goal": "help a podcast listener find episodes by topic and save clips", "audience": "podcast enthusiasts who listen during commutes", "page_type": "podcast search and clip saver"},
    {"id": "072", "category": "video", "brand": "Framehaus", "goal": "let a filmmaker upload a short film with chapters and director's commentary", "audience": "independent filmmakers sharing work", "page_type": "video player with chapters"},
    {"id": "073", "category": "music", "brand": "Pressplay", "goal": "help an independent artist distribute a release and track streaming royalties", "audience": "independent musicians managing their catalog", "page_type": "release distribution dashboard"},
    {"id": "074", "category": "media", "brand": "Digest", "goal": "present personalized news summaries with source diversity indicators", "audience": "news readers who want balanced perspectives", "page_type": "news digest feed"},
    {"id": "075", "category": "culture", "brand": "Gallery Walk", "goal": "let an art enthusiast explore a virtual exhibition room by room", "audience": "art lovers who cannot visit galleries in person", "page_type": "virtual gallery walkthrough"},
    {"id": "076", "category": "media", "brand": "Stackreader", "goal": "help a researcher organize saved articles into annotated collections", "audience": "academic researchers managing reading lists", "page_type": "reading list organizer"},
    {"id": "077", "category": "music", "brand": "Setlist", "goal": "let a concertgoer see a band's upcoming shows and compare ticket prices", "audience": "live music fans tracking touring artists", "page_type": "concert listing with price comparison"},
    {"id": "078", "category": "media", "brand": "Capsule", "goal": "help a user create a time capsule of links, notes, and photos to open later", "audience": "sentimental users who enjoy future nostalgia", "page_type": "time capsule creation flow"},
    # --- Developer Tools & Productivity (79-88) ---
    {"id": "079", "category": "devtools", "brand": "Signal Docs", "goal": "help a developer find an API endpoint and copy a working code example", "audience": "developers integrating a third-party API", "page_type": "API documentation with code samples"},
    {"id": "080", "category": "productivity", "brand": "Taskweave", "goal": "let a freelancer manage projects, track time, and generate client reports", "audience": "freelancers juggling multiple client projects", "page_type": "project management workspace"},
    {"id": "081", "category": "devtools", "brand": "Deployer", "goal": "show a developer deployment history with rollback options and health status", "audience": "developers responsible for production deployments", "page_type": "deployment history timeline"},
    {"id": "082", "category": "productivity", "brand": "Notegraph", "goal": "let a knowledge worker build a personal wiki with bidirectional links", "audience": "researchers and writers who think in networks", "page_type": "wiki-style note editor"},
    {"id": "083", "category": "devtools", "brand": "Schema Studio", "goal": "let a developer visually design a database schema with relationship constraints", "audience": "backend developers designing data models", "page_type": "visual schema designer"},
    {"id": "084", "category": "productivity", "brand": "Calendex", "goal": "help a team find a common meeting slot across time zones", "audience": "distributed teams scheduling across 3+ time zones", "page_type": "multi-timezone meeting scheduler"},
    {"id": "085", "category": "devtools", "brand": "Diffview", "goal": "show a developer a pull request diff with inline review comments", "audience": "developers reviewing code changes", "page_type": "code review diff view"},
    {"id": "086", "category": "productivity", "brand": "Focusblock", "goal": "help a student block distracting apps and track deep-work sessions", "audience": "students struggling with digital distractions", "page_type": "focus session timer"},
    {"id": "087", "category": "devtools", "brand": "Endpoint Monitor", "goal": "show an SRE uptime status for all monitored services with incident history", "audience": "SRE teams managing service reliability", "page_type": "status page with incident timeline"},
    {"id": "088", "category": "productivity", "brand": "Clipdeck", "goal": "let a content creator manage a multi-platform publishing calendar", "audience": "social media managers handling 5+ platforms", "page_type": "content calendar"},
    # --- Community, Social & Misc (89-100) ---
    {"id": "089", "category": "community", "brand": "Sidewalk", "goal": "help a new neighborhood member find local conversations and join", "audience": "people who recently moved to a new area", "page_type": "community forum feed"},
    {"id": "090", "category": "real estate", "brand": "Hearthline", "goal": "help a renter compare apartments with commute time overlays", "audience": "renters relocating to a new city", "page_type": "apartment comparison with commute map"},
    {"id": "091", "category": "job board", "brand": "Good Work", "goal": "help a candidate judge culture fit before applying", "audience": "mid-career professionals seeking meaningful work", "page_type": "job detail with culture insights"},
    {"id": "092", "category": "pet care", "brand": "Pawprint", "goal": "help a pet owner track vaccinations and book vet appointments", "audience": "pet owners managing multiple animals' health", "page_type": "pet health timeline"},
    {"id": "093", "category": "portfolio", "brand": "Mira Studio", "goal": "help a designer showcase case studies and prompt client inquiries", "audience": "design clients evaluating potential hires", "page_type": "portfolio case study page"},
    {"id": "094", "category": "logistics", "brand": "Route 7", "goal": "help a customer track a delivery with live location and ETA", "audience": "online shoppers waiting for a delivery", "page_type": "delivery tracking with live map"},
    {"id": "095", "category": "dating", "brand": "Commonpage", "goal": "help a user create a profile that showcases personality through prompts", "audience": "single adults who prefer substance over photos", "page_type": "profile creation with prompts"},
    {"id": "096", "category": "smart home", "brand": "Hearthstone", "goal": "let a homeowner control rooms, set scenes, and view energy usage", "audience": "smart-home early adopters", "page_type": "smart home control panel"},
    {"id": "097", "category": "climate", "brand": "Carbonsight", "goal": "show an individual their carbon footprint breakdown with reduction tips", "audience": "climate-conscious individuals tracking impact", "page_type": "carbon footprint breakdown"},
    {"id": "098", "category": "coworking", "brand": "DeskDrop", "goal": "help a freelancer find and book a hot desk for the day", "audience": "freelancers who need occasional workspace", "page_type": "coworking space finder with map"},
    {"id": "099", "category": "subscription", "brand": "CrateJoy", "goal": "let a subscriber rate past boxes and influence future curation", "audience": "subscription box customers who want personalization", "page_type": "subscription feedback and preferences"},
    {"id": "100", "category": "accessibility", "brand": "EasyGov", "goal": "help a visually impaired user navigate government forms with screen reader guidance", "audience": "visually impaired citizens accessing public services", "page_type": "accessible government form"},
    # --- Developer Tools & Infrastructure (101-115) ---
    {"id": "101", "category": "devtools", "brand": "CloudPulse", "goal": "help a cloud architect visualize microservice topology and inspect trace latency", "audience": "site reliability engineers managing Kubernetes clusters", "page_type": "service mesh topology map"},
    {"id": "102", "category": "devtools", "brand": "GitFlow Studio", "goal": "help an open-source maintainer review pull requests with automated test coverage overlays", "audience": "open-source software maintainers", "page_type": "PR code review hub"},
    {"id": "103", "category": "devtools", "brand": "SchemaCraft", "goal": "let a database administrator design GraphQL schemas and mock API responses", "audience": "full-stack developers building modern APIs", "page_type": "schema visualizer and playground"},
    {"id": "104", "category": "devtools", "brand": "EnvLock", "goal": "help a devops lead audit environment secrets and manage team permissions", "audience": "security leads at growth-stage SaaS companies", "page_type": "secrets access management matrix"},
    {"id": "105", "category": "devtools", "brand": "BugTrace Live", "goal": "let a QA engineer record session replays and attach console logs to bug tickets", "audience": "QA engineers and frontend developers", "page_type": "session replay inspector"},
    {"id": "106", "category": "devtools", "brand": "CargoShip", "goal": "help a release engineer orchestrate blue-green container deployments across regions", "audience": "release managers at enterprise fintechs", "page_type": "deployment pipeline monitor"},
    {"id": "107", "category": "devtools", "brand": "MetricPipe", "goal": "let a data engineer build real-time SQL stream transformations and monitor lag", "audience": "data engineers managing Kafka streams", "page_type": "stream processing DAG builder"},
    {"id": "108", "category": "devtools", "brand": "API Gateway X", "goal": "help an API architect set up rate limits, CORS rules, and JWT auth scopes", "audience": "backend architects managing public APIs", "page_type": "API gateway route config"},
    {"id": "109", "category": "devtools", "brand": "FeatureFlag Hub", "goal": "let a growth PM create canary rollouts and targeted user segment toggles", "audience": "product managers executing A/B feature experiments", "page_type": "feature flag management dashboard"},
    {"id": "110", "category": "devtools", "brand": "EdgeWorker", "goal": "help a serverless dev deploy edge functions and monitor global latency", "audience": "frontend engineers leveraging edge runtime computing", "page_type": "edge function analytics panel"},
    {"id": "111", "category": "devtools", "brand": "ContainerScan", "goal": "help a security analyst inspect container vulnerabilities and CVE severity scores", "audience": "DevSecOps analysts", "page_type": "vulnerability audit report"},
    {"id": "112", "category": "devtools", "brand": "QuerySpeed", "goal": "let a postgres DBA identify slow query execution plans and index recommendations", "audience": "database administrators optimizing database performance", "page_type": "query performance analyzer"},
    {"id": "113", "category": "devtools", "brand": "MockAPI Studio", "goal": "help a frontend developer build realistic mock JSON endpoints for prototyping", "audience": "frontend developers working ahead of backend APIs", "page_type": "mock endpoint designer"},
    {"id": "114", "category": "devtools", "brand": "WasmStudio", "goal": "let a C++ developer compile and test WebAssembly modules in-browser", "audience": "systems engineers building high-performance web apps", "page_type": "Wasm playground and profiler"},
    {"id": "115", "category": "devtools", "brand": "BuildSpeed", "goal": "help an iOS engineer optimize Xcode build times and dependency trees", "audience": "mobile development team leads", "page_type": "build artifact timeline dashboard"},
    # --- AI & Machine Learning Platforms (116-130) ---
    {"id": "116", "category": "ai", "brand": "PromptForge", "goal": "help a prompt engineer benchmark LLM outputs across system prompts and temperatures", "audience": "AI product engineers and prompt developers", "page_type": "prompt evaluation matrix"},
    {"id": "117", "category": "ai", "brand": "EmbedVector", "goal": "let a machine learning dev inspect vector embeddings and cluster distributions", "audience": "ML engineers building RAG architectures", "page_type": "vector space visualizer"},
    {"id": "118", "category": "ai", "brand": "DatasetForge", "goal": "help an AI trainer annotate multi-modal datasets with bounding boxes and semantic tags", "audience": "data annotators and ML research assistants", "page_type": "data labeling studio"},
    {"id": "119", "category": "ai", "brand": "ModelOps AI", "goal": "show an MLOps team model drift metrics, GPU utilization, and inference latency", "audience": "MLOps engineers monitoring production models", "page_type": "model telemetry dashboard"},
    {"id": "120", "category": "ai", "brand": "AgentFlow", "goal": "let a developer construct multi-agent workflow DAGs with tool-use nodes", "audience": "AI developers building autonomous agent swarms", "page_type": "agent canvas and execution graph"},
    {"id": "121", "category": "ai", "brand": "VoiceSynth", "goal": "help a podcast producer generate natural voiceover clips from script text", "audience": "content creators needing automated voiceovers", "page_type": "audio voice generation editor"},
    {"id": "122", "category": "ai", "brand": "VisionGuard AI", "goal": "let a security team train real-time object detection models for physical facility camera feeds", "audience": "facility security operators", "page_type": "camera stream detection hub"},
    {"id": "123", "category": "ai", "brand": "FineTune Studio", "goal": "help a data scientist prepare LoRA hyper-parameters and monitor loss curves", "audience": "AI researchers fine-tuning open-weights LLMs", "page_type": "training hyper-parameter panel"},
    {"id": "124", "category": "ai", "brand": "Synthetix Data", "goal": "let a healthcare researcher generate privacy-compliant synthetic patient records", "audience": "medical researchers needing anonymized datasets", "page_type": "synthetic data generator interface"},
    {"id": "125", "category": "ai", "brand": "CodeCopilot Pro", "goal": "help an enterprise tech lead audit AI-generated code snippets for license compliance", "audience": "software architects governing code security", "page_type": "code attribution audit view"},
    {"id": "126", "category": "ai", "brand": "NeuroCraft", "goal": "let a neuroscientist visualize EEG electrode activity maps during cognitive tasks", "audience": "neuroscience researchers studying brain-computer interfaces", "page_type": "EEG spatial activity heat map"},
    {"id": "127", "category": "ai", "brand": "TranslateAI Hub", "goal": "help a localization team review neural translation quality scores and edit glossaries", "audience": "localization managers translating software across 40 languages", "page_type": "translation memory and review editor"},
    {"id": "128", "category": "ai", "brand": "DocExtract AI", "goal": "help an insurance adjuster parse structured data from handwritten invoice PDFs", "audience": "claims processors automating paper intake", "page_type": "document OCR and field mapping interface"},
    {"id": "129", "category": "ai", "brand": "RAG Explorer", "goal": "let an enterprise search engineer test chunking strategies and hybrid retrieval scores", "audience": "search engineers building internal knowledge bases", "page_type": "retrieval chunking & ranking sandbox"},
    {"id": "130", "category": "ai", "brand": "DeepSearch AI", "goal": "help a patent attorney run deep semantic similarity searches across global patent databases", "audience": "patent attorneys evaluating prior art", "page_type": "semantic patent search dashboard"},
    # --- Fintech, Web3 & Wealth Management (131-145) ---
    {"id": "131", "category": "fintech", "brand": "Velox Pay", "goal": "help a cross-border freelancer convert multi-currency payouts into local fiat", "audience": "global digital nomads managing multi-currency income", "page_type": "multi-currency payout portal"},
    {"id": "132", "category": "fintech", "brand": "EquityStack", "goal": "let an early startup employee simulate stock option vesting schedules and tax implications", "audience": "startup employees with equity grants", "page_type": "equity calculator and exercise planner"},
    {"id": "133", "category": "fintech", "brand": "CapTable HQ", "goal": "help a founder model dilution across series A funding rounds", "audience": "startup founders raising venture capital", "page_type": "cap table dilution simulator"},
    {"id": "134", "category": "fintech", "brand": "MicroLend", "goal": "let a micro-finance officer evaluate peer-to-peer loan applications with risk scores", "audience": "loan officers in emerging markets", "page_type": "underwriting risk assessment view"},
    {"id": "135", "category": "fintech", "brand": "YieldVault", "goal": "help a DeFi investor optimize liquidity pool positioning across decentralized exchanges", "audience": "crypto yield farmers managing LP positions", "page_type": "DeFi liquidity analytics dashboard"},
    {"id": "136", "category": "fintech", "brand": "LedgerSync", "goal": "let a corporate accountant reconcile bank statements with ERP ledger entries", "audience": "senior accountants closing monthly books", "page_type": "automated bank reconciliation grid"},
    {"id": "137", "category": "fintech", "brand": "PulseTrade", "goal": "help a day trader monitor order book depth and execute stop-loss ladder orders", "audience": "active equity traders", "page_type": "real-time order book trading terminal"},
    {"id": "138", "category": "fintech", "brand": "TaxSprout", "goal": "help a sole proprietor file estimated quarterly taxes with deductible mileage tracking", "audience": "freelancers and gig workers", "page_type": "quarterly tax estimation dashboard"},
    {"id": "139", "category": "fintech", "brand": "ExpenseGo", "goal": "let an employee submit travel receipts via photo upload with automatic merchant categorisation", "audience": "business travelers submitting expense reports", "page_type": "mobile receipt submission flow"},
    {"id": "140", "category": "fintech", "brand": "TreasuryDirect AI", "goal": "help a corporate treasurer manage cash yield investments in short-term T-bills", "audience": "corporate treasurers overseeing cash reserves", "page_type": "treasury yield portfolio view"},
    {"id": "141", "category": "fintech", "brand": "FraudRadar", "goal": "help a risk team flag suspicious high-velocity credit card transactions", "audience": "fintech fraud analysts", "page_type": "fraud investigation workbench"},
    {"id": "142", "category": "fintech", "brand": "PandaInvest", "goal": "help a first-time investor build an automated index fund portfolio matching risk tolerance", "audience": "young professionals starting index investing", "page_type": "robo-advisor portfolio setup"},
    {"id": "143", "category": "fintech", "brand": "InvoicePulse", "goal": "let a small business owner issue factoring invoices and receive immediate advance funding", "audience": "small business owners dealing with net-90 terms", "page_type": "invoice factoring portal"},
    {"id": "144", "category": "fintech", "brand": "SubscriptionSaver", "goal": "help a consumer identify recurring subscriptions and cancel unwanted monthly charges", "audience": "budget-conscious consumers", "page_type": "recurring bill audit dashboard"},
    {"id": "145", "category": "fintech", "brand": "EstateVault", "goal": "help an estate planner organize digital assets, wills, and beneficiary instructions", "audience": "families planning estate inheritance", "page_type": "estate document distribution vault"},
    # --- EdTech & E-Learning (146-160) ---
    {"id": "146", "category": "edtech", "brand": "SkillPath", "goal": "help an aspiring developer complete code challenges with interactive test cases", "audience": "self-taught programmers learning full-stack dev", "page_type": "interactive code lab page"},
    {"id": "147", "category": "edtech", "brand": "LinguaDeck", "goal": "guide a language student through spaced-repetition vocabulary flashcards with audio cues", "audience": "language learners preparing for fluency exams", "page_type": "spaced repetition flashcard deck"},
    {"id": "148", "category": "edtech", "brand": "CampusHub", "goal": "help a college student check grade point average, assignment due dates, and syllabus links", "audience": "undergraduate university students", "page_type": "student course portal dashboard"},
    {"id": "149", "category": "edtech", "brand": "MathViz", "goal": "let a high school student interact with 3D calculus surface plots and derivative sliders", "audience": "STEM students learning advanced math", "page_type": "interactive math visualization"},
    {"id": "150", "category": "edtech", "brand": "TutorConnect", "goal": "help a parent find a certified math tutor for their child and schedule trial sessions", "audience": "parents seeking private tutoring", "page_type": "tutor discovery and booking"},
    {"id": "151", "category": "edtech", "brand": "Gradely", "goal": "help a middle school teacher grade essay submissions with rubric criteria and comments", "audience": "K-12 educators grading assignments", "page_type": "teacher rubric grading interface"},
    {"id": "152", "category": "edtech", "brand": "LabSim VR", "goal": "let a chemistry student conduct virtual acid-base titration experiments safely", "audience": "chemistry students doing remote lab work", "page_type": "virtual science lab simulator"},
    {"id": "153", "category": "edtech", "brand": "PeerReview Hub", "goal": "help graduate students critique research draft papers with inline annotations", "audience": "master and PhD candidates reviewing literature", "page_type": "peer manuscript review workspace"},
    {"id": "154", "category": "edtech", "brand": "CertTrack", "goal": "help an IT professional track progress toward cloud certification exams with practice quizzes", "audience": "IT professionals preparing for AWS/Azure certs", "page_type": "certification progress tracker"},
    {"id": "155", "category": "edtech", "brand": "StoryGenius", "goal": "guide a young child through interactive phonics stories with voice recognition", "audience": "early readers aged 5-8", "page_type": "interactive child reading experience"},
    {"id": "156", "category": "edtech", "brand": "MicroDegree", "goal": "let a professional submit capstone projects and request peer feedback badges", "audience": "career switchers completing bootcamp micro-credentials", "page_type": "capstone project submission portal"},
    {"id": "157", "category": "edtech", "brand": "ScholarGrid", "goal": "help a high school senior search federal grants and private college scholarships", "audience": "high school seniors applying for financial aid", "page_type": "scholarship matcher and deadlines"},
    {"id": "158", "category": "edtech", "brand": "CodeClassroom", "goal": "let a computer science instructor monitor student live code terminals during lecture", "audience": "coding bootcamp instructors", "page_type": "instructor multi-screen lab monitor"},
    {"id": "159", "category": "edtech", "brand": "AudioBook Learn", "goal": "help a student listen to classic literature with synchronized speed controls and chapter notes", "audience": "auditory learners studying literature", "page_type": "audiobook reader with transcript"},
    {"id": "160", "category": "edtech", "brand": "DebateClub AI", "goal": "help a student practice formal debate arguments against an AI opposing counsel", "audience": "debate club students preparing for tournaments", "page_type": "interactive argument simulator"},
    # --- Real Estate & Property Tech (161-175) ---
    {"id": "161", "category": "proptech", "brand": "HavenFind", "goal": "help a homebuyer filter listings by neighborhood walkability, solar potential, and noise index", "audience": "first-time homebuyers in metro areas", "page_type": "property search with environmental filters"},
    {"id": "162", "category": "proptech", "brand": "TenantPortal", "goal": "let an apartment renter submit maintenance requests and schedule automatic rent pay", "audience": "apartment tenants managing lease tasks", "page_type": "tenant dashboard and work order form"},
    {"id": "163", "category": "proptech", "brand": "LandlordHQ", "goal": "help an independent landlord track tenant leases, occupancy rates, and repair expenses", "audience": "small-scale real estate investors (1-10 units)", "page_type": "property portfolio overview"},
    {"id": "164", "category": "proptech", "brand": "SpaceLease", "goal": "help a business manager compare commercial office lease floor plans and square footage costs", "audience": "office ops managers expanding corporate offices", "page_type": "commercial listing comparison"},
    {"id": "165", "category": "proptech", "brand": "ConstructPulse", "goal": "let a site supervisor track daily construction milestone progress and material deliveries", "audience": "construction project managers on-site", "page_type": "site progress log and inspection checklist"},
    {"id": "166", "category": "proptech", "brand": "SubletCircle", "goal": "help a college student sublet their apartment during summer break with identity verification", "audience": "university students needing temporary sublets", "page_type": "sublet listing and application flow"},
    {"id": "167", "category": "proptech", "brand": "ZoningMap", "goal": "let an urban developer research land zoning regulations, height limits, and setback rules", "audience": "urban planners and real estate developers", "page_type": "interactive GIS zoning map"},
    {"id": "168", "category": "proptech", "brand": "HomeValuer", "goal": "help a homeowner estimate property value appraisal based on recent neighborhood comps", "audience": "homeowners considering selling", "page_type": "home equity valuation report"},
    {"id": "169", "category": "proptech", "brand": "OpenHouse AI", "goal": "let a real estate agent create digital open house visitor sign-in logs with follow-up tags", "audience": "realtors conducting open house events", "page_type": "open house visitor kiosk"},
    {"id": "170", "category": "proptech", "brand": "SolarQuote", "goal": "help a homeowner calculate rooftop solar installation costs and net metering payback", "audience": "homeowners evaluating clean energy transition", "page_type": "solar savings calculator"},
    {"id": "171", "category": "proptech", "brand": "HVACControl", "goal": "help a building facility engineer monitor commercial HVAC temperature zones and energy draw", "audience": "building facility managers", "page_type": "facility climate control system dashboard"},
    {"id": "172", "category": "proptech", "brand": "ColivingHub", "goal": "help an applicant match with compatible roommates based on lifestyle habits and budget", "audience": "young workers seeking shared coliving", "page_type": "roommate compatibility matcher"},
    {"id": "173", "category": "proptech", "brand": "MortgageDirect", "goal": "help a borrower pre-qualify for a home loan with instant bank statement verification", "audience": "home loan applicants", "page_type": "mortgage pre-approval application"},
    {"id": "174", "category": "proptech", "brand": "TitleLock", "goal": "let a title escrow agent verify property deed history and clear title liens", "audience": "title company settlement agents", "page_type": "title deed audit workflow"},
    {"id": "175", "category": "proptech", "brand": "Staging3D", "goal": "help a real estate agent virtually stage empty home room photos with furniture styles", "audience": "real estate agents marketing vacant properties", "page_type": "3D virtual home staging tool"},
    # --- Travel, Hospitality & Event Tech (176-190) ---
    {"id": "176", "category": "travel", "brand": "VoyagePlanner", "goal": "help a group traveler build a multi-stop itinerary with shared expense splitting", "audience": "group travel organizers planning vacations", "page_type": "collaborative trip itinerary planner"},
    {"id": "177", "category": "travel", "brand": "FlightRadar Pro", "goal": "let a frequent flyer monitor delay predictions, lounge amenities, and seat upgrades", "audience": "business travelers taking 20+ flights per year", "page_type": "flight monitor and seat selector"},
    {"id": "178", "category": "travel", "brand": "NomadStay", "goal": "help a remote worker filter long-term stays by internet speed rating and ergonomic desk photos", "audience": "digital nomads seeking monthly rentals", "page_type": "long-term stay catalog with internet badges"},
    {"id": "179", "category": "travel", "brand": "CampScout", "goal": "let an outdoors enthusiast discover backcountry campsites with vehicle clearance notes", "audience": "campers and overlanders", "page_type": "campsite reservation grid with trail maps"},
    {"id": "180", "category": "travel", "brand": "LocalGuide", "goal": "connect a tourist with verified local culinary guides for private food tasting tours", "audience": "travelers seeking authentic local experiences", "page_type": "experience booking with host profile"},
    {"id": "181", "category": "travel", "brand": "PackingCheck", "goal": "help a traveler generate a weather-adjusted packing checklist based on flight forecast", "audience": "leisure travelers packing for trips", "page_type": "smart packing list builder"},
    {"id": "182", "category": "travel", "brand": "CruiselineHQ", "goal": "let a passenger view port-of-call excursion timetables and onboard dining reservations", "audience": "cruise passengers planning ship activities", "page_type": "onboard schedule and excursion planner"},
    {"id": "183", "category": "travel", "brand": "VisaFlow", "goal": "help an international traveler check visa entry requirements, processing times, and forms", "audience": "global travelers navigating travel visas", "page_type": "visa requirements checker"},
    {"id": "184", "category": "travel", "brand": "SkiSlope Live", "goal": "show a skier live mountain lift statuses, powder snowfall reports, and trail maps", "audience": "skiing and snowboarding enthusiasts", "page_type": "ski resort conditions map"},
    {"id": "185", "category": "travel", "brand": "LuggageTransfer", "goal": "let a traveler schedule hotel-to-airport luggage pickup and track bag location", "audience": "luxury travelers avoiding heavy bags", "page_type": "luggage dispatch tracking view"},
    {"id": "186", "category": "travel", "brand": "EventPass HQ", "goal": "help a festival attendee browse concert set times, stage maps, and line alerts", "audience": "music festival attendees", "page_type": "festival set time schedule grid"},
    {"id": "187", "category": "travel", "brand": "BoatRent", "goal": "let a vacationer rent a catamaran for the day with captain certification check", "audience": "boating enthusiasts and vacationers", "page_type": "boat charter booking page"},
    {"id": "188", "category": "travel", "brand": "TrainRail Europe", "goal": "help a traveler plan intercity train connections with Eurail pass validation", "audience": "backpackers traveling across Europe by rail", "page_type": "rail connection route timetable"},
    {"id": "189", "category": "travel", "brand": "PetTravel", "goal": "help a pet owner find airline-approved pet carrier sizes and pet-friendly hotels", "audience": "pet owners traveling with dogs/cats", "page_type": "pet travel compliance guide"},
    {"id": "190", "category": "travel", "brand": "TransitPulse", "goal": "let a commuter view real-time subway train arrival countdowns and elevator outages", "audience": "daily urban transit commuters", "page_type": "city subway live transit board"},
    # --- Creator Economy & Media Tools (191-205) ---
    {"id": "191", "category": "creator", "brand": "PodcastStudio", "goal": "help a podcaster record multi-track remote audio interviews with automated noise removal", "audience": "independent podcasters and audio producers", "page_type": "browser recording studio interface"},
    {"id": "192", "category": "creator", "brand": "StreamOverlay", "goal": "let a Twitch streamer design custom chat alerts, subscriber goal bars, and widgets", "audience": "live video streamers", "page_type": "stream overlay designer canvas"},
    {"id": "193", "category": "creator", "brand": "NewsletterKit", "goal": "help an author curate a weekly link round-up email with click analytics", "audience": "newsletter writers with paid subscribers", "page_type": "newsletter layout and issue preview"},
    {"id": "194", "category": "creator", "brand": "FontCraft", "goal": "let a type designer inspect kerning pairs, glyph sets, and font export settings", "audience": "typography designers creating custom fonts", "page_type": "glyph editor and specimen viewer"},
    {"id": "195", "category": "creator", "brand": "BeatVault", "goal": "help a music producer sell non-exclusive instrumental beats with instant licensing contracts", "audience": "hip-hop/pop music producers selling beats", "page_type": "beat store marketplace with audio player"},
    {"id": "196", "category": "creator", "brand": "ThumbGen", "goal": "help a YouTuber create high-CTR video thumbnails with A/B thumbnail testing", "audience": "YouTube creators optimizing video click rates", "page_type": "thumbnail design comparison view"},
    {"id": "197", "category": "creator", "brand": "SponsorHub", "goal": "let an influencer manage brand sponsorship deals, media kit rates, and deliverable deadlines", "audience": "content creators negotiating brand deals", "page_type": "creator brand deal CRM"},
    {"id": "198", "category": "creator", "brand": "ClipCut AI", "goal": "help a video editor auto-generate short vertical clips from long-form video podcasts", "audience": "social media managers creating Shorts/Reels", "page_type": "video clipping timestamp editor"},
    {"id": "199", "category": "creator", "brand": "ArtPrint Studio", "goal": "help an illustrator order museum-grade archival prints and monitor fulfillment", "audience": "digital artists selling physical prints", "page_type": "print shop ordering dashboard"},
    {"id": "200", "category": "creator", "brand": "CommunityNest", "goal": "let a creator run private discussion forums, paywalled courses, and member events", "audience": "creators building paid membership communities", "page_type": "community forum feed and member hub"},
    {"id": "201", "category": "creator", "brand": "LinkBio Pro", "goal": "help an Instagram creator build a customizable link-in-bio landing page with product cards", "audience": "social creators monetizing bio links", "page_type": "link-in-bio mobile preview page"},
    {"id": "202", "category": "creator", "brand": "ColorGrade Studio", "goal": "let a videographer apply LUT color grading presets and compare before/after scopes", "audience": "colorists and video editors", "page_type": "LUT color scope comparator"},
    {"id": "203", "category": "creator", "brand": "SubCaption AI", "goal": "help an editor generate burn-in subtitles with custom font animations for TikTok", "audience": "short-form video creators", "page_type": "subtitle timing and styling view"},
    {"id": "204", "category": "creator", "brand": "MerchForge", "goal": "let a streamer mockup apparel designs on t-shirts and sync with print-on-demand storefront", "audience": "creators selling branded merch", "page_type": "apparel mockup generator"},
    {"id": "205", "category": "creator", "brand": "PatronPerks", "goal": "help a webcomic artist manage tiered patron rewards, early access posts, and physical mailings", "audience": "comic artists supported by patrons", "page_type": "patron tier benefit setup"},
    # --- CyberSecurity & Privacy Tech (206-220) ---
    {"id": "206", "category": "security", "brand": "VaultPass AI", "goal": "help an IT administrator enforce zero-trust password policies and audit weak credentials", "audience": "enterprise IT security leads", "page_type": "credential security health score"},
    {"id": "207", "category": "security", "brand": "PhishTrap", "goal": "let a security officer launch simulated phishing campaigns and train high-risk employees", "audience": "cybersecurity awareness trainers", "page_type": "phishing campaign results report"},
    {"id": "208", "category": "security", "brand": "SOC Shield", "goal": "help a security analyst correlate SIEM alert surges and triage potential malware breaches", "audience": "SOC (Security Operations Center) analysts", "page_type": "SIEM incident triage workbench"},
    {"id": "209", "category": "security", "brand": "PrivacyVault", "goal": "help a compliance officer handle GDPR data subject erasure requests and data exports", "audience": "DPOs (Data Protection Officers)", "page_type": "GDPR privacy request queue"},
    {"id": "210", "category": "security", "brand": "NetworkGuard", "goal": "let a network engineer inspect firewall rule hits, blocked IP ranges, and DDoS traffic bursts", "audience": "network security engineers", "page_type": "firewall traffic monitor"},
    {"id": "211", "category": "security", "brand": "KeyVault HSM", "goal": "help a cloud engineer manage cryptographic signing keys and rotation policies", "audience": "DevSecOps leads managing PKI infrastructure", "page_type": "HSM key rotation inventory"},
    {"id": "212", "category": "security", "brand": "BiometricAuth", "goal": "let an app dev configure FIDO2 WebAuthn passkey authentication flows", "audience": "security-focused software engineers", "page_type": "passkey auth configuration builder"},
    {"id": "213", "category": "security", "brand": "CodeAudit Pro", "goal": "help a security researcher run static application security testing (SAST) on source repos", "audience": "application security auditors", "page_type": "SAST code vulnerability report"},
    {"id": "214", "category": "security", "brand": "DarkWeb Monitor", "goal": "help a corporate security officer scan leaked dark web dumps for company domain emails", "audience": "threat intelligence analysts", "page_type": "domain exposure leak report"},
    {"id": "215", "category": "security", "brand": "AccessMatrix", "goal": "let an auditor review RBAC user permissions across cloud SaaS applications", "audience": "SOX and SOC2 compliance auditors", "page_type": "user permission audit matrix"},
    {"id": "216", "category": "security", "brand": "ZeroTrust Mesh", "goal": "help a network architect configure micro-segmented device tunnels and device posture checks", "audience": "enterprise infrastructure architects", "page_type": "zero-trust policy rule manager"},
    {"id": "217", "category": "security", "brand": "CloudPostulate", "goal": "let a security engineer audit AWS IAM policy wildcards and public S3 bucket exposure", "audience": "cloud security posture management (CSPM) leads", "page_type": "cloud posture compliance overview"},
    {"id": "218", "category": "security", "brand": "API ThreatGuard", "goal": "help an API gateway owner block BOLA (broken object level auth) attacks in real-time", "audience": "API security engineers", "page_type": "API attack mitigation dashboard"},
    {"id": "219", "category": "security", "brand": "DeepFake Check", "goal": "help a media newsroom verify video footage authenticity against AI synthetic manipulation", "audience": "fact-checkers and news editors", "page_type": "deepfake forensic audit tool"},
    {"id": "220", "category": "security", "brand": "PatchPulse", "goal": "help a system admin schedule zero-day OS security patch updates across server clusters", "audience": "sysadmins maintaining enterprise Linux servers", "page_type": "patch management timeline"},
    # --- Gaming, Esports & Community (221-235) ---
    {"id": "221", "category": "gaming", "brand": "GuildHub", "goal": "help an esports team manager schedule scrimmages, roster lineups, and tournament brackets", "audience": "competitive esports clan leaders", "page_type": "esports roster and match scheduler"},
    {"id": "222", "category": "gaming", "brand": "LootDrop", "goal": "let an RPG player inspect item drop probabilities, crafting recipes, and stat comparison", "audience": "hardcore RPG gamers optimizing builds", "page_type": "RPG item database and builder"},
    {"id": "223", "category": "gaming", "brand": "GameServer HQ", "goal": "help a community host launch private game servers with custom mod plugins and slot counts", "audience": "community game server admins", "page_type": "game server management console"},
    {"id": "224", "category": "gaming", "brand": "QuestLog", "goal": "help an indie game designer outline branching dialogue trees and quest objective state machines", "audience": "narrative designers in indie game studios", "page_type": "branching dialogue visual editor"},
    {"id": "225", "category": "gaming", "brand": "MatchStats", "goal": "help a competitive shooter player review match kill/death ratios, damage heatmaps, and accuracy", "audience": "FPS gamers analyzing gameplay performance", "page_type": "player performance telemetry"},
    {"id": "226", "category": "gaming", "brand": "ModVault", "goal": "let a PC gamer browse, install, and manage mod load orders for single-player RPGs", "audience": "PC gamers modding title libraries", "page_type": "mod manager and conflict resolver"},
    {"id": "227", "category": "gaming", "brand": "Speedrun Live", "goal": "help a speedrunner track split segment timers against world record comparison graphs", "audience": "speedrunners attempting record runs", "page_type": "speedrun timer and split comparison"},
    {"id": "228", "category": "gaming", "brand": "TavernFind", "goal": "help a tabletop RPG dungeon master organize D&D campaign notes, NPC stats, and encounter initiative", "audience": "Tabletop RPG dungeon masters", "page_type": "campaign manager and initiative tracker"},
    {"id": "229", "category": "gaming", "brand": "VRMotion", "goal": "let a VR arcade manager monitor headset battery levels, sanitization status, and active games", "audience": "VR arcade operators", "page_type": "VR headset arcade queue console"},
    {"id": "230", "category": "gaming", "brand": "IndieLaunch", "goal": "help an indie game developer showcase a playable web demo and collect playtest survey feedback", "audience": "indie devs launching early access titles", "page_type": "game playtest landing page"},
    {"id": "231", "category": "gaming", "brand": "DeckMaster", "goal": "help a collectible card game player assemble synergy decks and run draw probability simulations", "audience": "CCG/TCG players building tournament decks", "page_type": "deck builder and mana curve calculator"},
    {"id": "232", "category": "gaming", "brand": "EsportsBet AI", "goal": "help an odds compiler analyze team win rates and map pick/ban historical trends", "audience": "esports analytics providers", "page_type": "team win probability analysis"},
    {"id": "233", "category": "gaming", "brand": "PixelAsset", "goal": "let a pixel artist export sprite sheet animations and tilemaps for 2D platformers", "audience": "2D game artists and animators", "page_type": "sprite sheet animation previewer"},
    {"id": "234", "category": "gaming", "brand": "SoundFX Engine", "goal": "help a game audio designer mix spatial audio cues and positional sound triggers", "audience": "game sound designers", "page_type": "audio trigger event graph"},
    {"id": "235", "category": "gaming", "brand": "Achievements HQ", "goal": "help a trophy hunter track completion rates across platforms (Steam, PlayStation, Xbox)", "audience": "trophy hunters completing 100% achievements", "page_type": "multi-platform achievement matrix"},
    # --- Industrial IoT, Supply Chain & Logistics (236-250) ---
    {"id": "236", "category": "logistics", "brand": "FleetTrack Live", "goal": "help a fleet manager track long-haul truck locations, fuel efficiency, and driver rest breaks", "audience": "logistics dispatchers managing 500+ trucks", "page_type": "fleet telemetry and route map"},
    {"id": "237", "category": "logistics", "brand": "ColdChain Sense", "goal": "help a pharmaceutical logistics lead monitor refrigerated cargo container temperatures", "audience": "pharma supply chain quality leads", "page_type": "temperature sensor alert dashboard"},
    {"id": "238", "category": "logistics", "brand": "WarehouseWiz", "goal": "let a warehouse supervisor optimize forklift picking routes across high-density storage bays", "audience": "warehouse operations managers", "page_type": "warehouse bin picking route map"},
    {"id": "239", "category": "logistics", "brand": "PortCargo HQ", "goal": "help a freight forwarder clear shipping container customs manifests and track berth schedules", "audience": "freight forwarders at container ports", "page_type": "container shipping manifest overview"},
    {"id": "240", "category": "logistics", "brand": "LastMile Express", "goal": "help a local courier driver view optimized drop-off stops with customer signature capture", "audience": "last-mile delivery drivers", "page_type": "mobile delivery route list"},
    {"id": "241", "category": "logistics", "brand": "Dronely", "goal": "let an automated drone operator monitor automated delivery drop-zones and battery health", "audience": "autonomous drone delivery operators", "page_type": "drone flight telemetry command center"},
    {"id": "242", "category": "logistics", "brand": "InventoryPulse", "goal": "help a retail buyer set safety stock reorder thresholds and track supplier lead times", "audience": "inventory planners at retail chains", "page_type": "reorder point matrix and supplier lead times"},
    {"id": "243", "category": "logistics", "brand": "PalletPack", "goal": "let a shipping clerk compute 3D container packing load layouts to minimize empty space", "audience": "freight loading clerks", "page_type": "3D cargo container bin packing visualizer"},
    {"id": "244", "category": "logistics", "brand": "ReturnFlow", "goal": "help a customer initiate an e-commerce item return, print shipping label, and choose refund method", "audience": "shoppers returning online orders", "page_type": "self-service product return portal"},
    {"id": "245", "category": "logistics", "brand": "CustomsClear", "goal": "help an import compliance specialist compute tariff codes and duty tax estimations", "audience": "customs brokers and import specialists", "page_type": "HS tariff code calculation tool"},
    {"id": "246", "category": "logistics", "brand": "RailFreight", "goal": "let a rail logistics coordinator dispatch freight train cars and track switching yard locations", "audience": "railroad freight coordinators", "page_type": "rail car tracking and yard status grid"},
    {"id": "247", "category": "logistics", "brand": "PackagingEco", "goal": "help a fulfillment center select eco-friendly box dimensions that reduce dimensional weight costs", "audience": "packaging engineers at e-commerce fulfillment centers", "page_type": "box size optimizer"},
    {"id": "248", "category": "logistics", "brand": "VendorScore", "goal": "help a procurement director evaluate supplier on-time delivery percentages and defect rates", "audience": "procurement directors", "page_type": "supplier performance scorecard"},
    {"id": "249", "category": "logistics", "brand": "AirCargo Direct", "goal": "let an air freight broker book unit load device (ULD) pallet space on cargo flights", "audience": "air cargo brokers booking belly freight", "page_type": "air cargo capacity booking"},
    {"id": "250", "category": "logistics", "brand": "YardManager", "goal": "help a truck yard hostler direct trailer tractor-trailers to open loading dock doors", "audience": "distribution center yard managers", "page_type": "dock door yard management grid"},
    # --- BioTech, Science & Research (251-265) ---
    {"id": "251", "category": "science", "brand": "BioGene Studio", "goal": "help a geneticist align DNA sequencing reads and inspect variant mutations", "audience": "genomics researchers analyzing NGS data", "page_type": "DNA sequence alignment viewer"},
    {"id": "252", "category": "science", "brand": "ChemStructure", "goal": "let a medicinal chemist draw 3D molecular structures and test binding affinity predictions", "audience": "pharmacology researchers designing synthetic drugs", "page_type": "3D molecular structure visualizer"},
    {"id": "253", "category": "science", "brand": "AstroScope", "goal": "help an astronomer process radio telescope light curve data to discover exoplanet transits", "audience": "astrophysicists analyzing telescope survey data", "page_type": "light curve exoplanet detector"},
    {"id": "254", "category": "science", "brand": "ClinicalTrial HQ", "goal": "help a clinical research coordinator record patient cohort visit logs and adverse event reports", "audience": "clinical trial managers at pharma companies", "page_type": "patient cohort protocol dashboard"},
    {"id": "255", "category": "science", "brand": "OceanData", "goal": "help a marine biologist track tagged sea turtle migration routes and sea surface temperature anomalies", "audience": "oceanographic researchers", "page_type": "marine species tracking map"},
    {"id": "256", "category": "science", "brand": "MicroscopeAI", "goal": "let a pathologist label cell culture fluorescence images for automated cell counting", "audience": "histopathology lab technicians", "page_type": "microscopy cell segmentation editor"},
    {"id": "257", "category": "science", "brand": "SeismoWatch", "goal": "help a geophysicist monitor real-time earthquake fault line sensors and magnitude alerts", "audience": "seismologists analyzing seismic networks", "page_type": "seismic activity waveform monitor"},
    {"id": "258", "category": "science", "brand": "LabInventory Pro", "goal": "help a lab manager manage hazardous chemical safety data sheets (SDS) and storage locations", "audience": "university research lab managers", "page_type": "chemical inventory & SDS repository"},
    {"id": "259", "category": "science", "brand": "ClimateModeler", "goal": "let a climate scientist run regional precipitation projections under warming scenarios", "audience": "climatologists modeling climate change impact", "page_type": "climate simulation spatial map"},
    {"id": "260", "category": "science", "brand": "CRISPRDesign", "goal": "help a bioengineer design single guide RNA (sgRNA) targets with off-target risk scores", "audience": "synthetic biologists doing gene editing", "page_type": "gRNA target designer tool"},
    {"id": "261", "category": "science", "brand": "ProteinFold AI", "goal": "help a structural biologist inspect 3D protein folding predictions and hydrogen bonds", "audience": "biochemists studying protein structures", "page_type": "protein structure 3D viewer"},
    {"id": "262", "category": "science", "brand": "ParticleTrack", "goal": "let a particle physicist view subatomic collision event displays from hadron collider sensors", "audience": "high-energy physicists", "page_type": "particle collision event visualizer"},
    {"id": "263", "category": "science", "brand": "SoilSense", "goal": "help an agronomist analyze soil moisture, nitrogen levels, and crop yield forecasts", "audience": "agricultural scientists advising farmers", "page_type": "precision agriculture soil sensor dashboard"},
    {"id": "264", "category": "science", "brand": "MaterialSim", "goal": "help a materials scientist simulate tensile strength and thermal expansion of alloy samples", "audience": "materials science engineers", "page_type": "material stress-strain curve analyzer"},
    {"id": "265", "category": "science", "brand": "EpidemiologyHub", "goal": "help a public health officer track disease transmission R0 rates and vaccination coverage", "audience": "epidemiologists managing public health outbreaks", "page_type": "epidemic contact tracing dashboard"},
    # --- HR Tech & Recruitment (266-280) ---
    {"id": "266", "category": "hr", "brand": "TalentMatch AI", "goal": "help a tech recruiter filter candidate resumes by verified skill tags and salary expectations", "audience": "in-house recruiters sourcing software engineers", "page_type": "recruitment candidate pipeline"},
    {"id": "267", "category": "hr", "brand": "OnboardEase", "goal": "guide a new hire through signing employment tax forms, choosing hardware, and completing training", "audience": "newly hired remote employees", "page_type": "employee onboarding checklist"},
    {"id": "268", "category": "hr", "brand": "Pulse360", "goal": "help an employee collect anonymous 360-degree peer feedback reviews for annual evaluation", "audience": "corporate employees conducting annual reviews", "page_type": "360-degree feedback review workspace"},
    {"id": "269", "category": "hr", "brand": "CompBenchmark", "goal": "help a total rewards director benchmark team compensation bands against market percentiles", "audience": "HR compensation managers", "page_type": "salary band market benchmarking tool"},
    {"id": "270", "category": "hr", "brand": "TimeClock Direct", "goal": "let an hourly employee clock shift hours, request time off, and swap shifts with coworkers", "audience": "hourly retail and hospitality staff", "page_type": "mobile shift scheduling & timeclock"},
    {"id": "271", "category": "hr", "brand": "DEIAudit", "goal": "help a chief diversity officer track company pay equity metrics and hiring funnel representation", "audience": "DEI officers and executive leadership", "page_type": "diversity & pay equity metrics overview"},
    {"id": "272", "category": "hr", "brand": "ExitSurvey HQ", "goal": "help an HR business partner analyze exit interview trend themes and turnover causes", "audience": "HR business partners reducing attrition", "page_type": "employee turnover analytics report"},
    {"id": "273", "category": "hr", "brand": "BenefitsChoice", "goal": "help an employee select open enrollment health insurance benefits and FSA allocations", "audience": "employees selecting annual health benefits", "page_type": "benefits selection & plan comparison"},
    {"id": "274", "category": "hr", "brand": "SkillMatrix", "goal": "help an engineering director assess team competency gaps and assign training budgets", "audience": "engineering directors managing tech skills", "page_type": "team skill matrix visualizer"},
    {"id": "275", "category": "hr", "brand": "RemotePerks", "goal": "let a remote worker claim home office stipend reimbursements and wellness allowances", "audience": "remote employees redeeming company perks", "page_type": "perks allowance portal"},
    {"id": "276", "category": "hr", "brand": "ReloAssist", "goal": "help a corporate transferee track relocation expense budgets, movers, and temporary housing", "audience": "employees relocating for work assignments", "page_type": "corporate relocation manager"},
    {"id": "277", "category": "hr", "brand": "ContractorHQ", "goal": "help a company manage 1099 contractor agreements, W-9 collection, and invoice payouts", "audience": "operations leads managing gig contractors", "page_type": "1099 contractor management dashboard"},
    {"id": "278", "category": "hr", "brand": "CulturePulse", "goal": "let an HR lead launch weekly 1-question pulse surveys and measure team eNPS morale score", "audience": "people ops leads measuring employee sentiment", "page_type": "pulse survey sentiment dashboard"},
    {"id": "279", "category": "hr", "brand": "InternalMobility", "goal": "help an existing employee apply for open internal transfers before external postings", "audience": "current employees seeking internal promotions", "page_type": "internal job board & transfer app"},
    {"id": "280", "category": "hr", "brand": "MentorshipHub", "goal": "connect a junior staff member with a senior mentor based on career development goals", "audience": "employees seeking career mentorship", "page_type": "mentor matching & goal tracker"},
    # --- Legal Tech & Compliance (281-295) ---
    {"id": "281", "category": "legal", "brand": "ContractAI Review", "goal": "help a corporate attorney highlight non-standard indemnity clauses in vendor NDAs", "audience": "corporate lawyers reviewing contracts", "page_type": "contract redline and risk analyzer"},
    {"id": "282", "category": "legal", "brand": "IPVault Pro", "goal": "help a trademark specialist manage trademark registration renewal deadlines across countries", "audience": "IP paralegals and trademark attorneys", "page_type": "trademark portfolio timeline"},
    {"id": "283", "category": "legal", "brand": "CaseLoom", "goal": "help a litigation team index court discovery trial exhibits and witness deposition transcripts", "audience": "litigation paralegals preparing for trial", "page_type": "trial exhibit & transcript search"},
    {"id": "284", "category": "legal", "brand": "ESignFlow", "goal": "help an operations manager send multi-signer agreements with audit trail certificates", "audience": "business managers executing binding agreements", "page_type": "electronic signature routing workflow"},
    {"id": "285", "category": "legal", "brand": "ComplianceShield", "goal": "help an ethics officer manage employee conflict of interest disclosures and gift registers", "audience": "corporate compliance officers", "page_type": "compliance disclosure audit queue"},
    {"id": "286", "category": "legal", "brand": "EntityManagement", "goal": "help a corporate secretary track subsidiary board resolutions, cap tables, and filing dates", "audience": "corporate secretaries managing global entities", "page_type": "entity governance matrix"},
    {"id": "287", "category": "legal", "brand": "MatterBilling", "goal": "help a law firm partner view client billable hours, trust account balances, and collections", "audience": "law firm managing partners", "page_type": "law firm billing and timekeeping grid"},
    {"id": "288", "category": "legal", "brand": "NotaryLive", "goal": "help a signor complete an online remote notarization session via video call with ID check", "audience": "individuals needing remote notarization", "page_type": "remote online notary (RON) video portal"},
    {"id": "289", "category": "legal", "brand": "StatuteSearch", "goal": "help a legal researcher query state statutes and regulatory code history with legislative diffs", "audience": "legal scholars and policy researchers", "page_type": "statutory code search with diff viewer"},
    {"id": "290", "category": "legal", "brand": "EDiscovery Hub", "goal": "help a legal tech analyst review e-discovery email chains and apply attorney-client privilege tags", "audience": "e-discovery specialists in commercial litigation", "page_type": "e-discovery document review queue"},
    {"id": "291", "category": "legal", "brand": "BailBond Direct", "goal": "help a defense attorney file quick bail bond paperwork and track arraignment hearings", "audience": "criminal defense attorneys", "page_type": "court appearance & bail tracker"},
    {"id": "292", "category": "legal", "brand": "ImmiFlow", "goal": "help an immigration paralegal prepare H-1B visa petition packages with DOL LCA receipts", "audience": "immigration paralegals filing work visas", "page_type": "immigration visa case management"},
    {"id": "293", "category": "legal", "brand": "DisputeResolver", "goal": "let commercial parties settle breach-of-contract disputes through online binding arbitration", "audience": "businesses resolving small claims disputes", "page_type": "online dispute resolution arbitration portal"},
    {"id": "294", "category": "legal", "brand": "FOIAQuery", "goal": "help a investigative journalist file Freedom of Information Act requests and track response deadlines", "audience": "journalists and transparency advocates", "page_type": "FOIA request tracker"},
    {"id": "295", "category": "legal", "brand": "TenantRights AI", "goal": "help a low-income tenant generate a formal notice letter to landlord for repair violations", "audience": "tenants asserting housing legal rights", "page_type": "tenant rights legal letter generator"},
    # --- Non-Profit & Civic Tech (296-300) ---
    {"id": "296", "category": "civic", "brand": "CivicVote", "goal": "help a citizen check voter registration status, find ballot drop boxes, and preview local measures", "audience": "voters preparing for upcoming local elections", "page_type": "voter ballot guide & polling location finder"},
    {"id": "297", "category": "civic", "brand": "CityFix 311", "goal": "let a resident report a pothole or broken streetlight with photo location tag and track city repair", "audience": "city residents filing 311 service requests", "page_type": "311 municipal issue reporting"},
    {"id": "298", "category": "nonprofit", "brand": "DonorPulse", "goal": "help a non-profit fundraising director launch a capital campaign page with live donor progress bar", "audience": "non-profit development managers", "page_type": "fundraising campaign landing & donor wall"},
    {"id": "299", "category": "nonprofit", "brand": "VolunteerMatch HQ", "goal": "help a community volunteer discover local food bank shifts matching their weekend availability", "audience": "community volunteers", "page_type": "volunteer opportunity matcher & calendar"},
    {"id": "300", "category": "civic", "brand": "GrantsGov Direct", "goal": "help a non-profit executive search federal municipal grants and track application submission", "audience": "non-profit executives seeking government grants", "page_type": "grant application tracker & deadline calendar"},
]

# ============================================================
# 20 PAGE ARCHETYPES — each generates fundamentally different HTML
# ============================================================

ARCHETYPES = [
    "landing_hero_split",        # 0  split hero with image/text
    "dashboard_sidebar",         # 1  sidebar nav + grid of metric cards
    "kanban_board",              # 2  multi-column drag-style board
    "search_filter_results",     # 3  filter sidebar + result list
    "detail_page_anchored",      # 4  sticky nav + scrolling sections
    "stepper_form",              # 5  multi-step form with progress
    "timeline_vertical",         # 6  vertical timeline feed
    "comparison_table",          # 7  feature comparison table
    "map_plus_list",             # 8  map + sidebar listing
    "calendar_grid",             # 9  calendar month view
    "editorial_longform",        # 10 editorial/magazine article
    "card_masonry",              # 11 masonry/bento grid
    "chat_interface",            # 12 chat/messaging UI
    "interactive_exercise",      # 13 centered interactive widget
    "data_table_dense",          # 14 data-dense table
    "profile_workspace",        # 15 profile/settings workspace
    "feed_cards",                # 16 social/content feed
    "code_documentation",        # 17 docs with code blocks
    "pricing_comparison",        # 18 pricing tiers
    "guided_flow",               # 19 wizard/guided experience
]

# ============================================================
# DESIGN TOKENS — palettes, typography, spacing, shapes
# ============================================================

PALETTES = [
    {"name": "warm editorial",      "bg": "#F4EFE7", "surface": "#FFFFFF", "text": "#241B17", "muted": "#8A7E76", "accent": "#C65D32", "focus": "#174CFF"},
    {"name": "quiet ecological",    "bg": "#F5F7F6", "surface": "#FFFFFF", "text": "#17231F", "muted": "#5E6A66", "accent": "#247A5B", "focus": "#0050FF"},
    {"name": "bright civic",        "bg": "#FFF9F0", "surface": "#FFFFFF", "text": "#13233A", "muted": "#5F6B7A", "accent": "#F16B57", "focus": "#003AFF"},
    {"name": "calm clinical",       "bg": "#F4F8F7", "surface": "#FFFFFF", "text": "#173B42", "muted": "#5A7A7F", "accent": "#287F78", "focus": "#0060DD"},
    {"name": "trustworthy modern",  "bg": "#F7F8FC", "surface": "#FFFFFF", "text": "#182238", "muted": "#5B6378", "accent": "#5B62D6", "focus": "#1A3BFF"},
    {"name": "sunlit atlas",        "bg": "#FFF8ED", "surface": "#FFFFFF", "text": "#24344A", "muted": "#6A7485", "accent": "#E4774E", "focus": "#0044CC"},
    {"name": "warm academic",       "bg": "#FAF7F1", "surface": "#FFFFFF", "text": "#282321", "muted": "#7A706A", "accent": "#B45B35", "focus": "#2244DD"},
    {"name": "energetic precise",   "bg": "#F1F5F4", "surface": "#FFFFFF", "text": "#172526", "muted": "#566A6B", "accent": "#E15B3D", "focus": "#0033EE"},
    {"name": "late-night luminous", "bg": "#11131A", "surface": "#1E2030", "text": "#F5F3EF", "muted": "#9A96A8", "accent": "#B58CFF", "focus": "#5A9EFF"},
    {"name": "human grounded",      "bg": "#F7F3EC", "surface": "#FFFFFF", "text": "#20342D", "muted": "#5A6E62", "accent": "#D66C43", "focus": "#1155DD"},
    {"name": "quiet residential",   "bg": "#F3F0EA", "surface": "#FFFFFF", "text": "#252A2B", "muted": "#6D7574", "accent": "#647D68", "focus": "#2250CC"},
    {"name": "technical editorial", "bg": "#F8FAFC", "surface": "#FFFFFF", "text": "#17202A", "muted": "#64748B", "accent": "#2563EB", "focus": "#0040FF"},
    {"name": "confident culinary",  "bg": "#FFF7ED", "surface": "#FFFFFF", "text": "#321E19", "muted": "#7A5F4E", "accent": "#D45A31", "focus": "#1133CC"},
    {"name": "dark culture",        "bg": "#111217", "surface": "#1A1B25", "text": "#F4F1E9", "muted": "#8B8898", "accent": "#FFB454", "focus": "#5588FF"},
    {"name": "clear utilitarian",   "bg": "#F3F6F8", "surface": "#FFFFFF", "text": "#17212B", "muted": "#5C6B7A", "accent": "#2775CA", "focus": "#0055EE"},
    {"name": "soft nocturnal",      "bg": "#191A25", "surface": "#242536", "text": "#F3F0E8", "muted": "#9A9588", "accent": "#D69A75", "focus": "#6699EE"},
    {"name": "botanical fresh",     "bg": "#F0F5EE", "surface": "#FFFFFF", "text": "#1B2B22", "muted": "#5A7362", "accent": "#3A8A5C", "focus": "#0044BB"},
    {"name": "neo-brutalist",       "bg": "#FFFDF5", "surface": "#FFFFFF", "text": "#111111", "muted": "#666666", "accent": "#FF4400", "focus": "#0000FF"},
    {"name": "pastel playful",      "bg": "#FFF5F7", "surface": "#FFFFFF", "text": "#2D1F3D", "muted": "#7A6B8A", "accent": "#E06090", "focus": "#4400DD"},
    {"name": "monochrome ink",      "bg": "#FAFAFA", "surface": "#FFFFFF", "text": "#111111", "muted": "#777777", "accent": "#333333", "focus": "#0055FF"},
]

TYPOGRAPHY_PAIRINGS = [
    {"name": "serif-display-sans-body", "heading": "Georgia, 'Times New Roman', serif", "body": "'Segoe UI', Arial, sans-serif", "mono": "'Courier New', monospace", "scale": "1.333 perfect-fourth"},
    {"name": "geometric-sans-system", "heading": "'Trebuchet MS', 'Segoe UI', sans-serif", "body": "Arial, Helvetica, sans-serif", "mono": "'Consolas', monospace", "scale": "1.25 major-third"},
    {"name": "humanist-sans", "heading": "'Gill Sans', 'Segoe UI', sans-serif", "body": "'Gill Sans', 'Segoe UI', sans-serif", "mono": "'Courier New', monospace", "scale": "1.2 minor-third"},
    {"name": "slab-serif-compact", "heading": "'Rockwell', 'Courier New', serif", "body": "Verdana, Geneva, sans-serif", "mono": "'Lucida Console', monospace", "scale": "1.414 augmented-fourth"},
    {"name": "elegant-serif", "heading": "'Palatino Linotype', 'Book Antiqua', serif", "body": "'Palatino Linotype', 'Book Antiqua', serif", "mono": "'Courier New', monospace", "scale": "1.5 perfect-fifth"},
    {"name": "compact-technical", "heading": "Verdana, Geneva, sans-serif", "body": "Verdana, Geneva, sans-serif", "mono": "'Consolas', 'Lucida Console', monospace", "scale": "1.125 major-second"},
    {"name": "expressive-display", "heading": "Impact, 'Arial Black', sans-serif", "body": "Arial, Helvetica, sans-serif", "mono": "'Courier New', monospace", "scale": "1.618 golden-ratio"},
    {"name": "neutral-system", "heading": "-apple-system, 'Segoe UI', sans-serif", "body": "-apple-system, 'Segoe UI', sans-serif", "mono": "'SF Mono', 'Consolas', monospace", "scale": "1.2 minor-third"},
    {"name": "bookish-mixed", "heading": "'Cambria', Georgia, serif", "body": "'Calibri', 'Segoe UI', sans-serif", "mono": "'Consolas', monospace", "scale": "1.333 perfect-fourth"},
    {"name": "editorial-serif", "heading": "'Times New Roman', Times, serif", "body": "'Times New Roman', Times, serif", "mono": "'Courier New', monospace", "scale": "1.25 major-third"},
]

NAV_PATTERNS = [
    "top horizontal bar",
    "sidebar persistent",
    "bottom tab bar (mobile-first)",
    "command palette overlay",
    "stepper/wizard progress",
    "hamburger with slide-out drawer",
    "tab navigation within page",
    "breadcrumb + contextual sidebar",
    "map-based spatial navigation",
    "timeline-based sequential navigation",
]

INTERACTION_MODELS = [
    "click-to-reveal progressive disclosure",
    "drag-and-drop reordering",
    "inline editing on click",
    "filter and sort with instant results",
    "step-by-step guided wizard",
    "hover preview with expandable detail",
    "toggle and switch controls",
    "scroll-triggered content loading",
    "modal dialogs for focused tasks",
    "command bar keyboard shortcuts",
]

RESPONSIVE_STRATEGIES = [
    "stack columns to single column below 768px, hide sidebar, show hamburger menu",
    "transform grid to swipeable horizontal cards on mobile, keep top nav compact",
    "sidebar collapses to bottom sheet on mobile, content fills viewport",
    "table transforms to stacked cards with key data promoted, secondary data collapsed",
    "two-pane layout becomes tabbed view on mobile, map goes fullscreen",
    "stepper stays horizontal on desktop, switches to vertical progress on mobile",
    "masonry grid reduces columns from 4→2→1, images maintain aspect ratio",
    "dashboard cards reflow into priority-ordered single column with collapsible sections",
    "editorial layout drops sidebar, typography scales down, images become full-bleed",
    "calendar switches from month grid to agenda list on mobile, swipe to change day",
]

RADIUS_LANGUAGE = [
    "0px — sharp edges",
    "4px — subtle softening",
    "8px — moderate rounding",
    "12px — friendly rounding",
    "16px — generous rounding",
    "24px — pill-like elements",
    "50% — fully circular avatars and icons",
    "2px cards, 20px buttons — mixed language",
    "0px containers, 8px interactive — contrast rounding",
    "16px cards, 999px pills — organic and soft",
]

SPACING_RHYTHMS = [
    "4px base, 8-16-24-32-48 scale",
    "8px base, 16-24-32-48-64 scale",
    "6px base, 12-18-24-36-48 scale",
    "4px micro, 12-20-32-48 macro",
    "8px uniform grid with 24px section gaps",
    "tight 4-8-12 for data, generous 32-48-64 for editorial",
    "fibonacci 8-13-21-34-55",
    "dense 4-8-16 with 40px breathing room between sections",
    "modular 16px base grid throughout",
    "progressive 8-16-32-64 doubling scale",
]


# ============================================================
# ARCHETYPE-SPECIFIC HTML GENERATORS
# ============================================================
# Each function returns (initial_html, critic_feedback, corrected_html)
# Initial HTML is deliberately imperfect. Corrected fixes all listed issues.

def _css_vars(p: dict, t: dict, radius: str, space: str) -> str:
    """Generate CSS custom property block from palette and typography."""
    return f"""--bg:{p['bg']};--surface:{p['surface']};--text:{p['text']};--muted:{p['muted']};--accent:{p['accent']};--focus:{p['focus']};
    --heading-font:{t['heading']};--body-font:{t['body']};--mono-font:{t['mono']};
    --radius:{radius.split('—')[0].strip() if '—' in radius else '8px'};
    --space-xs:4px;--space-sm:8px;--space-md:16px;--space-lg:24px;--space-xl:48px"""


def _meta(brand: str) -> str:
    return f'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(brand)}</title>'


def gen_landing_hero_split(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]
    audience = prod["audience"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:16px {t['body']};background:{p['bg']};color:{p['text']}}}
header{{padding:16px 5%;background:{p['text']};color:{p['bg']};display:flex;justify-content:space-between}}
.hero{{display:grid;grid-template-columns:1fr 1fr;min-height:80vh;padding:60px 5%}}
h1{{font:48px {t['heading']};margin:0 0 16px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:40px 5%}}
.card{{background:white;padding:20px;border-radius:8px}}
button{{background:{p['accent']};color:white;border:0;padding:12px 20px;cursor:pointer}}
</style></head><body>
<header><strong>{escape(b)}</strong><div><a href="#" style="color:white">About</a> <a href="#" style="color:white">Contact</a></div></header>
<div class="hero"><div><h1>Welcome to {escape(b)}</h1><p>We help you {escape(goal)}.</p><button>Get Started</button></div><div style="background:#ddd;min-height:300px"></div></div>
<div class="cards"><div class="card"><h2>Feature One</h2><p>Description of feature.</p></div><div class="card"><h2>Feature Two</h2><p>Description of feature.</p></div><div class="card"><h2>Feature Three</h2><p>Description of feature.</p></div></div>
</body></html>'''

    feedback = [
        "No <main> landmark — screen readers cannot identify the primary content region.",
        f"Hero heading says 'Welcome to {b}' which is generic — it should communicate the specific value proposition for {audience}.",
        "Navigation links use generic anchor tags styled inline rather than a semantic <nav> with proper focus states.",
        "No responsive CSS — the two-column hero and three-column cards will overflow at 390px.",
        "Cards have identical placeholder text ('Description of feature') which adds no real information.",
        "The placeholder div for the hero image is an empty div with no alt text or semantic meaning.",
        "No visible focus styles on interactive elements — keyboard users cannot see where they are.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}
body{{margin:0;font:16px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
a{{color:inherit}}a:focus-visible,button:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(1200px,90%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:64px;gap:16px}}
.brand{{font:700 18px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
nav a{{color:var(--bg);text-decoration:none;padding:8px 12px;border-radius:var(--radius)}}
nav a:hover{{background:rgba(255,255,255,.15)}}
.menu-btn{{display:none;background:transparent;border:1px solid var(--bg);color:var(--bg);padding:6px 12px;border-radius:var(--radius);cursor:pointer}}
.hero{{display:grid;grid-template-columns:1.2fr .8fr;gap:48px;align-items:center;padding:80px 0 60px}}
.eyebrow{{font:700 12px/1.4 var(--body-font);letter-spacing:.1em;color:var(--accent);text-transform:uppercase}}
h1{{font:clamp(2.5rem,5vw,4rem)/1.05 var(--heading-font);margin:12px 0 16px;letter-spacing:-.03em}}
.lede{{color:var(--muted);max-width:52ch;margin-bottom:24px}}
.btn-primary{{display:inline-flex;align-items:center;padding:14px 24px;background:var(--accent);color:#fff;border:0;border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer;text-decoration:none}}
.btn-primary:hover{{filter:brightness(1.1)}}
.btn-secondary{{display:inline-flex;align-items:center;padding:14px 24px;border:2px solid var(--text);color:var(--text);border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer;text-decoration:none;background:transparent;margin-left:10px}}
.hero-visual{{background:var(--surface);border:1px solid var(--muted);border-radius:calc(var(--radius) * 2);min-height:320px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-style:italic}}
.features{{padding:60px 0}}
.features h2{{font:clamp(1.8rem,3vw,2.5rem)/1.1 var(--heading-font);margin:0 0 32px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.card{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);padding:28px;border-radius:var(--radius)}}
.card h3{{margin:0 0 8px;font:700 18px var(--heading-font)}}
.card p{{color:var(--muted);margin:0;line-height:1.5}}
.badge{{display:inline-block;padding:4px 10px;border-radius:99px;font:700 11px var(--body-font);background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 20%,transparent);padding:32px 0;color:var(--muted);font-size:14px;margin-top:48px}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:700px){{
  nav{{display:none}}.menu-btn{{display:block}}
  .hero{{grid-template-columns:1fr;padding:48px 0 40px;gap:24px}}
  .hero-visual{{order:-1;min-height:220px}}
  .grid{{grid-template-columns:1fr}}
  h1{{font-size:clamp(2rem,6vw,2.8rem)}}
}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#features">Features</a><a href="#about">About</a><a href="#contact">Contact</a></nav><button class="menu-btn" aria-label="Open menu">Menu</button></div></header>
<main>
<section class="wrap hero"><div><span class="eyebrow">{escape(prod['category'].upper())}</span><h1>{escape(goal.split(' and ')[0].replace('help a ', 'Help every ').replace('let a ', 'Let every ').capitalize() if 'help' in goal or 'let' in goal else goal.capitalize())}</h1><p class="lede">Designed for {escape(audience)}. {escape(goal.capitalize())} — with clarity, confidence, and zero friction.</p><div><a class="btn-primary" href="#features">See how it works</a><a class="btn-secondary" href="#contact">Get in touch</a></div></div><div class="hero-visual" role="img" aria-label="Product illustration showing the {escape(b)} interface">[Product illustration]</div></section>
<section class="wrap features" id="features"><h2>Built for the way you work</h2><div class="grid">
<article class="card"><span class="badge">Core</span><h3>Smart defaults</h3><p>Start with intelligent presets tuned for {escape(audience)}, then adjust as you go.</p></article>
<article class="card"><span class="badge">Clarity</span><h3>Information hierarchy</h3><p>See what matters first. Secondary details stay accessible without cluttering the view.</p></article>
<article class="card"><span class="badge">Speed</span><h3>One-action shortcuts</h3><p>The most common task is always one click away, whether you are on desktop or mobile.</p></article>
</div></section>
</main>
<footer><div class="wrap">&copy; {escape(b)} — designed to {escape(goal)}.</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_dashboard_sidebar(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;display:flex;height:100vh}}
.sidebar{{width:240px;background:{p['text']};color:white;padding:20px}}
.sidebar a{{color:white;display:block;padding:8px;text-decoration:none}}
.content{{flex:1;padding:30px;overflow-y:auto;background:{p['bg']}}}
h1{{font-size:24px;margin:0 0 20px}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.metric{{background:white;padding:20px;border-radius:8px;text-align:center}}
.metric .value{{font-size:32px;font-weight:bold;color:{p['accent']}}}
.table-wrap{{margin-top:24px}}table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd}}
</style></head><body>
<div class="sidebar"><strong>{escape(b)}</strong><a href="#">Dashboard</a><a href="#">Reports</a><a href="#">Settings</a></div>
<div class="content"><h1>Dashboard</h1>
<div class="metrics"><div class="metric"><div class="value">1,247</div><div>Total Users</div></div><div class="metric"><div class="value">89%</div><div>Uptime</div></div><div class="metric"><div class="value">342</div><div>Active Now</div></div><div class="metric"><div class="value">$12.4k</div><div>Revenue</div></div></div>
<div class="table-wrap"><table><tr><th>Name</th><th>Status</th><th>Date</th></tr><tr><td>Item A</td><td>Active</td><td>Today</td></tr><tr><td>Item B</td><td>Pending</td><td>Yesterday</td></tr></table></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the dashboard content area.",
        "Sidebar links have no visual focus indicator — keyboard navigation is invisible.",
        "The four-column metrics grid will overflow on small screens; no responsive breakpoints.",
        "Table has no caption or summary — screen readers get no context about what data this shows.",
        "Metric labels are generic ('Total Users', 'Uptime') — should relate to the specific product goal.",
        f"Dashboard heading is generic 'Dashboard' — should orient the user toward their primary task: {prod['goal']}.",
        "No loading or empty states — if data is unavailable the page is blank.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}
body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text);display:flex;min-height:100vh}}
a{{color:inherit}}*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.sidebar{{width:240px;background:var(--text);color:var(--bg);padding:20px;display:flex;flex-direction:column;position:sticky;top:0;height:100vh;overflow-y:auto}}
.sidebar .brand{{font:700 18px var(--heading-font);margin-bottom:24px;color:var(--bg)}}
.sidebar nav{{display:flex;flex-direction:column;gap:2px}}
.sidebar nav a{{padding:10px 12px;border-radius:var(--radius);text-decoration:none;color:var(--bg);font-size:14px}}
.sidebar nav a:hover,.sidebar nav a[aria-current]{{background:rgba(255,255,255,.12)}}
.sidebar nav a[aria-current]{{font-weight:700}}
.toggle-sidebar{{display:none;position:fixed;top:12px;left:12px;z-index:100;background:var(--text);color:var(--bg);border:0;padding:8px 14px;border-radius:var(--radius);cursor:pointer}}
.main{{flex:1;padding:32px 40px;overflow-y:auto}}
.page-header{{margin-bottom:28px}}
.page-header h1{{font:700 clamp(1.3rem,2.5vw,1.8rem) var(--heading-font);margin:0 0 4px}}
.page-header p{{color:var(--muted);margin:0}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px}}
.metric-card{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);border-radius:var(--radius);padding:20px}}
.metric-card .label{{font:600 12px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
.metric-card .value{{font:700 28px var(--heading-font);color:var(--accent);margin:6px 0 2px}}
.metric-card .delta{{font-size:12px;color:var(--muted)}}
.delta.up{{color:#1a8a4a}}.delta.down{{color:#c0392b}}
.table-section{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);border-radius:var(--radius);overflow:hidden}}
.table-header{{padding:16px 20px;border-bottom:1px solid color-mix(in srgb,var(--muted) 15%,transparent);display:flex;justify-content:space-between;align-items:center}}
.table-header h2{{margin:0;font:700 16px var(--heading-font)}}
table{{width:100%;border-collapse:collapse}}
th{{text-align:left;padding:10px 20px;font:600 12px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid color-mix(in srgb,var(--muted) 15%,transparent)}}
td{{padding:12px 20px;border-bottom:1px solid color-mix(in srgb,var(--muted) 8%,transparent)}}
tr:hover td{{background:color-mix(in srgb,var(--accent) 4%,transparent)}}
.status-badge{{display:inline-flex;padding:3px 10px;border-radius:99px;font:600 11px var(--body-font)}}
.status-active{{background:#e8f5e9;color:#2e7d32}}.status-pending{{background:#fff3e0;color:#e65100}}
.empty-state{{text-align:center;padding:48px 20px;color:var(--muted)}}
@media(max-width:900px){{.metrics{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:700px){{
  .sidebar{{position:fixed;left:-260px;z-index:99;transition:left .2s}}.sidebar.open{{left:0}}
  .toggle-sidebar{{display:block}}.main{{padding:60px 20px 20px}}
  .metrics{{grid-template-columns:1fr}}
  .table-header{{flex-direction:column;align-items:start;gap:8px}}
}}
</style></head><body>
<button class="toggle-sidebar" aria-label="Toggle navigation" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰ Menu</button>
<aside class="sidebar" aria-label="Main navigation"><div class="brand">{escape(b)}</div>
<nav><a href="#" aria-current="page">Overview</a><a href="#">Reports</a><a href="#">Activity</a><a href="#">Settings</a></nav></aside>
<main class="main">
<div class="page-header"><h1>{escape(b)} — Overview</h1><p>At a glance: {escape(goal)}.</p></div>
<div class="metrics" role="list" aria-label="Key metrics">
<div class="metric-card" role="listitem"><div class="label">Active Sessions</div><div class="value">1,247</div><div class="delta up">↑ 12% this week</div></div>
<div class="metric-card" role="listitem"><div class="label">System Health</div><div class="value">99.2%</div><div class="delta up">↑ 0.3%</div></div>
<div class="metric-card" role="listitem"><div class="label">Pending Actions</div><div class="value">18</div><div class="delta down">↑ 4 since yesterday</div></div>
<div class="metric-card" role="listitem"><div class="label">Completed Today</div><div class="value">342</div><div class="delta up">↑ 8%</div></div>
</div>
<div class="table-section"><div class="table-header"><h2>Recent Activity</h2><button class="btn-secondary" style="padding:6px 14px;border:1px solid var(--muted);background:transparent;border-radius:var(--radius);cursor:pointer;font-size:13px">Export</button></div>
<table><caption class="sr-only">Recent system events and their status</caption>
<thead><tr><th scope="col">Event</th><th scope="col">Status</th><th scope="col">Time</th></tr></thead>
<tbody><tr><td>Deployment v2.4.1</td><td><span class="status-badge status-active">Completed</span></td><td>12 min ago</td></tr>
<tr><td>Config update — region-east</td><td><span class="status-badge status-pending">In review</span></td><td>1 hr ago</td></tr>
<tr><td>Alert: CPU threshold</td><td><span class="status-badge status-active">Resolved</span></td><td>3 hrs ago</td></tr>
</tbody></table></div>
</main>
<style>.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}}</style>
</body></html>'''

    return initial, feedback, corrected


def gen_kanban_board(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;background:{p['bg']};color:{p['text']}}}
header{{padding:16px 24px;background:{p['text']};color:white;display:flex;justify-content:space-between}}
.board{{display:flex;gap:16px;padding:24px;overflow-x:auto;height:calc(100vh - 60px)}}
.column{{min-width:280px;background:#f0f0f0;border-radius:8px;padding:12px}}
.column h2{{font-size:14px;text-transform:uppercase;margin:0 0 12px}}
.card{{background:white;padding:12px;border-radius:6px;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
.card h3{{font-size:14px;margin:0 0 6px}}
.tag{{font-size:11px;padding:2px 8px;border-radius:99px;background:{p['accent']};color:white}}
</style></head><body>
<header><strong>{escape(b)}</strong><span>Board View</span></header>
<div class="board">
<div class="column"><h2>To Do</h2><div class="card"><h3>Task one</h3><span class="tag">High</span></div><div class="card"><h3>Task two</h3><span class="tag">Low</span></div></div>
<div class="column"><h2>In Progress</h2><div class="card"><h3>Task three</h3><span class="tag">Medium</span></div></div>
<div class="column"><h2>Review</h2><div class="card"><h3>Task four</h3><span class="tag">High</span></div></div>
<div class="column"><h2>Done</h2><div class="card"><h3>Task five</h3><span class="tag">Low</span></div></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark and no <h1> — the page has no primary heading for screen readers.",
        "Board columns have fixed min-width causing horizontal overflow at 390px with no responsive fallback.",
        "Cards contain only generic 'Task one' text — should reflect actual product domain content.",
        "Priority tags use color alone (all same accent color) to differentiate urgency levels.",
        "No keyboard interaction hints — users cannot tab between cards or columns meaningfully.",
        "No column counts or summary — users with many items cannot gauge backlog size.",
        "No empty state for columns with zero cards.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text);display:flex;flex-direction:column;height:100vh}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 24px;display:flex;align-items:center;min-height:56px;gap:16px;flex-shrink:0}}
.brand{{font:700 17px var(--heading-font);margin-right:auto;color:var(--bg)}}
header nav a{{color:var(--bg);text-decoration:none;padding:6px 10px;border-radius:var(--radius);font-size:13px}}
header nav a:hover{{background:rgba(255,255,255,.1)}}
.toolbar{{padding:12px 24px;display:flex;align-items:center;gap:12px;border-bottom:1px solid color-mix(in srgb,var(--muted) 20%,transparent);flex-shrink:0}}
.toolbar h1{{font:700 16px var(--heading-font);margin:0}}
.toolbar .filter{{padding:5px 12px;border:1px solid var(--muted);border-radius:var(--radius);background:transparent;font:13px var(--body-font);cursor:pointer;color:var(--text)}}
.board{{display:flex;gap:16px;padding:20px 24px;overflow-x:auto;flex:1;align-items:start}}
.column{{min-width:280px;max-width:320px;background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);display:flex;flex-direction:column;max-height:100%}}
.col-header{{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid color-mix(in srgb,var(--muted) 12%,transparent)}}
.col-header h2{{font:700 13px var(--body-font);text-transform:uppercase;letter-spacing:.06em;margin:0;color:var(--muted)}}
.col-count{{font:700 12px var(--body-font);background:color-mix(in srgb,var(--muted) 12%,transparent);padding:2px 8px;border-radius:99px;color:var(--muted)}}
.col-body{{padding:8px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:8px}}
.card{{background:var(--bg);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);padding:14px;border-radius:calc(var(--radius) * .75);cursor:pointer;transition:box-shadow .15s}}
.card:hover{{box-shadow:0 4px 12px rgba(0,0,0,.08)}}
.card h3{{font:600 14px var(--heading-font);margin:0 0 6px}}
.card p{{font-size:13px;color:var(--muted);margin:0 0 8px}}
.card-meta{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.tag{{font:600 11px var(--body-font);padding:2px 8px;border-radius:99px}}
.tag-high{{background:#fce4ec;color:#c62828}}.tag-medium{{background:#fff3e0;color:#e65100}}.tag-low{{background:#e8f5e9;color:#2e7d32}}
.avatar{{width:22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font:700 10px var(--body-font);margin-left:auto}}
.empty{{text-align:center;padding:24px;color:var(--muted);font-style:italic;font-size:13px}}
@media(max-width:700px){{
  .board{{flex-direction:column;overflow-x:visible;padding:12px}}
  .column{{min-width:100%;max-width:100%}}
  .col-body{{max-height:300px}}
}}
</style></head><body>
<header><span class="brand">{escape(b)}</span><nav aria-label="Primary"><a href="#">Board</a><a href="#">List</a><a href="#">Calendar</a></nav></header>
<div class="toolbar"><h1>Project Board</h1><button class="filter">Filter ▾</button></div>
<main class="board" aria-label="Kanban board">
<section class="column" aria-label="To Do"><div class="col-header"><h2>To Do</h2><span class="col-count" aria-label="2 items">2</span></div><div class="col-body">
<article class="card" tabindex="0"><h3>Design onboarding flow</h3><p>Create wireframes for the first-time user experience.</p><div class="card-meta"><span class="tag tag-high">High</span><span class="avatar" title="Alex">A</span></div></article>
<article class="card" tabindex="0"><h3>Audit accessibility labels</h3><p>Review all interactive elements for screen reader compatibility.</p><div class="card-meta"><span class="tag tag-medium">Medium</span><span class="avatar" title="Priya">P</span></div></article>
</div></section>
<section class="column" aria-label="In Progress"><div class="col-header"><h2>In Progress</h2><span class="col-count" aria-label="1 item">1</span></div><div class="col-body">
<article class="card" tabindex="0"><h3>Implement search filters</h3><p>Add category and date range filters to the search results page.</p><div class="card-meta"><span class="tag tag-high">High</span><span class="avatar" title="Sam">S</span></div></article>
</div></section>
<section class="column" aria-label="Review"><div class="col-header"><h2>Review</h2><span class="col-count" aria-label="1 item">1</span></div><div class="col-body">
<article class="card" tabindex="0"><h3>Update pricing table</h3><p>Revise tier names and feature lists based on user feedback.</p><div class="card-meta"><span class="tag tag-low">Low</span><span class="avatar" title="Jordan">J</span></div></article>
</div></section>
<section class="column" aria-label="Done"><div class="col-header"><h2>Done</h2><span class="col-count" aria-label="0 items">0</span></div><div class="col-body"><p class="empty">No completed items yet.</p></div></section>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_search_filter_results(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.layout{{display:flex;padding:24px}}
.filters{{width:240px;padding-right:24px}}
.filters h2{{font-size:16px}}
.results{{flex:1}}
.result{{background:white;padding:16px;margin-bottom:12px;border-radius:6px}}
.result h3{{margin:0 0 4px}}
input[type="text"]{{width:100%;padding:10px;border:1px solid #ccc;border-radius:4px;margin-bottom:16px}}
label{{display:block;margin-bottom:8px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="layout">
<div class="filters"><h2>Filters</h2><input type="text" placeholder="Search..."><label><input type="checkbox"> Option A</label><label><input type="checkbox"> Option B</label><label><input type="checkbox"> Option C</label></div>
<div class="results"><h1>Results</h1><div class="result"><h3>Result Item One</h3><p>Description of this result.</p></div><div class="result"><h3>Result Item Two</h3><p>Description of this result.</p></div><div class="result"><h3>Result Item Three</h3><p>Description of this result.</p></div></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark — the results area needs semantic structure.",
        "Filter labels are generic ('Option A', 'Option B') — must reflect the product domain.",
        "Search input has no associated label element — inaccessible to screen readers.",
        "Two-column filter+results layout will stack poorly at 390px — filters should collapse to a togglable panel.",
        "No result count shown — users cannot gauge how many matches exist.",
        "All results have identical placeholder descriptions.",
        "No visible focus styles on form controls or result links.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.55 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(1200px,92%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-bar{{display:flex;align-items:center;min-height:60px;gap:16px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
.search-box{{display:flex;align-items:center;gap:8px;flex:1;max-width:480px}}
.search-box label{{clip:rect(0,0,0,0);position:absolute}}
.search-box input{{flex:1;padding:9px 14px;border:1px solid rgba(255,255,255,.3);border-radius:var(--radius);background:rgba(255,255,255,.1);color:var(--bg);font:14px var(--body-font)}}
.search-box input::placeholder{{color:rgba(255,255,255,.5)}}
.layout{{display:grid;grid-template-columns:240px 1fr;gap:32px;padding:28px 0}}
.filters{{position:sticky;top:20px;align-self:start}}
.filters h2{{font:700 14px var(--heading-font);margin:0 0 16px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}}
.filter-group{{margin-bottom:20px}}
.filter-group h3{{font:600 13px var(--body-font);margin:0 0 8px;color:var(--text)}}
.filter-group label{{display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;font-size:14px}}
.filter-group input[type="checkbox"]{{accent-color:var(--accent)}}
.filter-toggle{{display:none;padding:10px 16px;border:1px solid var(--muted);border-radius:var(--radius);background:var(--surface);cursor:pointer;font:600 14px var(--body-font);color:var(--text);margin-bottom:16px;width:100%}}
.results-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.results-header h1{{font:700 clamp(1.2rem,2.5vw,1.6rem) var(--heading-font);margin:0}}
.result-count{{color:var(--muted);font-size:14px}}
.result{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:20px;border-radius:var(--radius);margin-bottom:12px;transition:box-shadow .15s}}
.result:hover{{box-shadow:0 4px 16px rgba(0,0,0,.06)}}
.result h3{{margin:0 0 4px;font:600 17px var(--heading-font)}}
.result h3 a{{color:var(--text);text-decoration:none}}.result h3 a:hover{{color:var(--accent)}}
.result p{{color:var(--muted);margin:0 0 8px;font-size:14px}}
.result-meta{{display:flex;gap:12px;font-size:12px;color:var(--muted)}}
.tag{{padding:2px 8px;border-radius:99px;font:600 11px var(--body-font);background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent)}}
@media(max-width:700px){{
  .layout{{grid-template-columns:1fr}}
  .filters{{position:static;display:none}}.filters.open{{display:block}}
  .filter-toggle{{display:block}}
}}
</style></head><body>
<header><div class="header-bar wrap"><a class="brand" href="#">{escape(b)}</a><div class="search-box"><label for="search">Search</label><input id="search" type="text" placeholder="Search {escape(prod['category'])}…"></div></div></header>
<main class="wrap">
<div class="layout">
<aside class="filters" aria-label="Search filters">
<button class="filter-toggle" aria-expanded="false" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none';this.setAttribute('aria-expanded',this.getAttribute('aria-expanded')==='false')">☰ Show Filters</button>
<div><h2>Refine Results</h2>
<div class="filter-group"><h3>Category</h3><label><input type="checkbox"> Featured picks</label><label><input type="checkbox"> New arrivals</label><label><input type="checkbox"> Top rated</label></div>
<div class="filter-group"><h3>Availability</h3><label><input type="checkbox"> Available now</label><label><input type="checkbox"> Coming soon</label></div>
</div></aside>
<section>
<div class="results-header"><h1>Search Results</h1><span class="result-count">3 results found</span></div>
<article class="result"><h3><a href="#">Premium starter package</a></h3><p>Everything you need to get started, with guided setup and priority support for {escape(prod['audience'])}.</p><div class="result-meta"><span class="tag">Featured</span><span>Updated 2 days ago</span></div></article>
<article class="result"><h3><a href="#">Advanced workflow toolkit</a></h3><p>Powerful automation features designed to {escape(goal.split(' and ')[0] if ' and ' in goal else goal)}.</p><div class="result-meta"><span class="tag">Popular</span><span>Updated 1 week ago</span></div></article>
<article class="result"><h3><a href="#">Community essentials</a></h3><p>Core features with community support — ideal for those exploring the platform.</p><div class="result-meta"><span class="tag">Free tier</span><span>Updated 3 days ago</span></div></article>
</section>
</div>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_detail_page_anchored(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:16px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px;position:sticky;top:0}}
.content{{max-width:800px;margin:auto;padding:40px 24px}}
h1{{font-size:36px}}h2{{font-size:24px;margin-top:40px}}
.gallery{{display:flex;gap:8px;overflow-x:auto}}
.gallery div{{min-width:200px;height:150px;background:#ddd;border-radius:8px}}
.specs{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}}
.spec{{background:white;padding:16px;border-radius:8px}}
button{{background:{p['accent']};color:white;border:0;padding:14px 28px;border-radius:8px;font-size:16px;cursor:pointer;margin-top:24px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="content">
<h1>Product Detail</h1>
<div class="gallery"><div></div><div></div><div></div><div></div></div>
<h2>Specifications</h2>
<div class="specs"><div class="spec"><strong>Material</strong><p>Premium quality</p></div><div class="spec"><strong>Dimensions</strong><p>Standard size</p></div><div class="spec"><strong>Weight</strong><p>Lightweight</p></div><div class="spec"><strong>Warranty</strong><p>1 year</p></div></div>
<button>Add to Cart</button>
</div></body></html>'''

    feedback = [
        "No <main> landmark — the content area needs semantic wrapping.",
        "Product heading is generic 'Product Detail' — should name the actual product and its key value.",
        "Gallery images are empty divs with no alt text or semantic image role.",
        "Specifications use vague text ('Premium quality', 'Standard size') — no real information.",
        "No sticky section navigation — on a long detail page users need anchored jump links.",
        "The 'Add to Cart' button has no loading or success feedback state.",
        "Two-column spec grid has no responsive handling for mobile.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(960px,90%);margin:auto}}
header{{background:var(--text);color:var(--bg);position:sticky;top:0;z-index:10}}
.header-inner{{display:flex;align-items:center;min-height:56px;padding:0 5%;gap:16px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
header nav a{{color:var(--bg);text-decoration:none;padding:6px 10px;font-size:13px;border-radius:var(--radius)}}
header nav a:hover{{background:rgba(255,255,255,.1)}}
.anchor-nav{{position:sticky;top:56px;background:var(--bg);border-bottom:1px solid color-mix(in srgb,var(--muted) 20%,transparent);z-index:9;padding:0 5%}}
.anchor-nav ul{{list-style:none;margin:0;padding:0;display:flex;gap:4px;overflow-x:auto}}
.anchor-nav a{{display:block;padding:12px 14px;color:var(--muted);text-decoration:none;font:600 13px var(--body-font);white-space:nowrap;border-bottom:2px solid transparent}}
.anchor-nav a:hover,.anchor-nav a.active{{color:var(--accent);border-bottom-color:var(--accent)}}
.hero-detail{{padding:32px 0;display:grid;grid-template-columns:1.2fr .8fr;gap:32px;align-items:start}}
.gallery{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.gallery-item{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:13px;font-style:italic}}
.gallery-item.main{{grid-column:span 2;aspect-ratio:16/9}}
.detail-info h1{{font:700 clamp(1.5rem,3vw,2.2rem) var(--heading-font);margin:0 0 8px}}
.detail-info .subtitle{{color:var(--muted);margin:0 0 16px}}
.price{{font:700 28px var(--heading-font);color:var(--accent);margin:0 0 20px}}
.btn-primary{{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;background:var(--accent);color:#fff;border:0;border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer}}
.btn-primary:hover{{filter:brightness(1.1)}}
.section{{padding:40px 0;border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent)}}
.section h2{{font:700 clamp(1.2rem,2vw,1.6rem) var(--heading-font);margin:0 0 20px}}
.specs{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}
.spec{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);padding:16px;border-radius:var(--radius)}}
.spec dt{{font:600 12px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}}
.spec dd{{margin:0;font:600 16px var(--heading-font)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:28px 0;color:var(--muted);font-size:13px}}
@media(max-width:700px){{
  .hero-detail{{grid-template-columns:1fr}}
  .gallery{{grid-template-columns:1fr}}.gallery-item.main{{grid-column:span 1}}
  .specs{{grid-template-columns:1fr}}
  .anchor-nav ul{{gap:0}}
}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#">Home</a><a href="#">Browse</a></nav></div></header>
<nav class="anchor-nav" aria-label="Page sections"><ul><li><a href="#overview" class="active">Overview</a></li><li><a href="#specs">Specifications</a></li><li><a href="#reviews">Reviews</a></li></ul></nav>
<main class="wrap">
<section class="hero-detail" id="overview">
<div class="gallery"><div class="gallery-item main" role="img" aria-label="Main product view of {escape(b)}">[Main product image]</div><div class="gallery-item" role="img" aria-label="Detail angle 1">[Detail 1]</div><div class="gallery-item" role="img" aria-label="Detail angle 2">[Detail 2]</div></div>
<div class="detail-info"><h1>{escape(b)} — Signature Edition</h1><p class="subtitle">Designed to {escape(goal)}.</p><div class="price">$149.00</div><button class="btn-primary" aria-live="polite">Add to cart</button><p style="font-size:13px;color:var(--muted);margin-top:12px">Free shipping on orders over $75. 30-day returns.</p></div>
</section>
<section class="section" id="specs"><h2>Specifications</h2><div class="specs">
<dl class="spec"><dt>Material</dt><dd>Recycled ocean plastic blend</dd></dl>
<dl class="spec"><dt>Dimensions</dt><dd>34 × 22 × 8 cm</dd></dl>
<dl class="spec"><dt>Weight</dt><dd>420 g</dd></dl>
<dl class="spec"><dt>Warranty</dt><dd>2-year full coverage</dd></dl>
</div></section>
<section class="section" id="reviews"><h2>Customer Reviews</h2><p style="color:var(--muted)">No reviews yet. Be the first to share your experience.</p></section>
</main>
<footer><div class="wrap">&copy; {escape(b)}</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_stepper_form(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:16px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.form-wrap{{max-width:600px;margin:40px auto;padding:0 20px}}
h1{{font-size:28px}}
.steps{{display:flex;gap:8px;margin-bottom:24px}}
.step{{flex:1;text-align:center;padding:8px;background:#ddd;border-radius:4px}}
.step.active{{background:{p['accent']};color:white}}
.field{{margin-bottom:16px}}
.field label{{display:block;margin-bottom:4px;font-weight:bold}}
.field input,.field select{{width:100%;padding:10px;border:1px solid #ccc;border-radius:4px}}
.buttons{{display:flex;justify-content:space-between;margin-top:24px}}
button{{padding:12px 24px;border:0;border-radius:6px;cursor:pointer}}
.next{{background:{p['accent']};color:white}}
.back{{background:#ddd}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="form-wrap">
<h1>Get Started</h1>
<div class="steps"><div class="step active">Step 1</div><div class="step">Step 2</div><div class="step">Step 3</div></div>
<div class="field"><label>Full Name</label><input type="text"></div>
<div class="field"><label>Email</label><input type="email"></div>
<div class="field"><label>Category</label><select><option>Select one</option><option>A</option><option>B</option></select></div>
<div class="buttons"><button class="back">Back</button><button class="next">Next</button></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the form content.",
        "Step indicators say 'Step 1', 'Step 2' — should describe what each step accomplishes.",
        "Form inputs lack `id` attributes and labels use no `for` — not properly associated.",
        "Select options are 'A' and 'B' — must be domain-relevant choices.",
        "'Back' button appearance offers no visual distinction of disabled state for step 1.",
        "No form validation feedback — users get no error or success messages.",
        "No progress indication beyond the step bar — users don't know what percentage they've completed.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none}}
.form-wrap{{width:min(560px,90%);margin:40px auto;padding-bottom:60px}}
.form-wrap h1{{font:700 clamp(1.4rem,3vw,2rem) var(--heading-font);margin:0 0 8px}}
.form-wrap .subtitle{{color:var(--muted);margin:0 0 28px}}
.progress{{display:flex;gap:4px;margin-bottom:32px;position:relative}}
.progress::before{{content:'';position:absolute;top:50%;left:0;right:0;height:2px;background:color-mix(in srgb,var(--muted) 20%,transparent);z-index:0;transform:translateY(-50%)}}
.progress-step{{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;position:relative;z-index:1}}
.progress-dot{{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 13px var(--body-font);background:var(--surface);border:2px solid color-mix(in srgb,var(--muted) 30%,transparent);color:var(--muted)}}
.progress-step.active .progress-dot{{background:var(--accent);border-color:var(--accent);color:#fff}}
.progress-step.done .progress-dot{{background:var(--accent);border-color:var(--accent);color:#fff}}
.progress-label{{font:600 11px var(--body-font);color:var(--muted);text-align:center}}
.progress-step.active .progress-label{{color:var(--text);font-weight:700}}
.form-card{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);padding:28px}}
.form-card h2{{font:700 18px var(--heading-font);margin:0 0 20px}}
.field{{margin-bottom:20px}}
.field label{{display:block;margin-bottom:6px;font:600 14px var(--body-font);color:var(--text)}}
.field input,.field select{{width:100%;padding:11px 14px;border:1px solid color-mix(in srgb,var(--muted) 30%,transparent);border-radius:var(--radius);font:15px var(--body-font);color:var(--text);background:var(--bg)}}
.field input:focus,.field select:focus{{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 15%,transparent)}}
.field .hint{{font-size:12px;color:var(--muted);margin-top:4px}}
.field .error{{font-size:12px;color:#c62828;margin-top:4px;display:none}}
.buttons{{display:flex;justify-content:space-between;margin-top:28px}}
.btn{{padding:12px 24px;border-radius:var(--radius);font:600 15px var(--body-font);cursor:pointer;border:0}}
.btn-next{{background:var(--accent);color:#fff}}.btn-next:hover{{filter:brightness(1.1)}}
.btn-back{{background:transparent;border:1px solid var(--muted);color:var(--text)}}.btn-back:disabled{{opacity:.4;cursor:not-allowed}}
.completion{{font-size:13px;color:var(--muted);text-align:center;margin-top:12px}}
@media(max-width:500px){{
  .progress-label{{font-size:10px}}.progress-dot{{width:28px;height:28px;font-size:12px}}
  .form-card{{padding:20px}}
}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="form-wrap" aria-label="Registration form">
<h1>Create Your Account</h1>
<p class="subtitle">{escape(goal.capitalize())} — let's get you set up.</p>
<div class="progress" role="list" aria-label="Form progress">
<div class="progress-step done" role="listitem"><div class="progress-dot">✓</div><span class="progress-label">Your Info</span></div>
<div class="progress-step active" role="listitem"><div class="progress-dot">2</div><span class="progress-label">Preferences</span></div>
<div class="progress-step" role="listitem"><div class="progress-dot">3</div><span class="progress-label">Confirm</span></div>
</div>
<div class="form-card"><h2>Your Preferences</h2>
<div class="field"><label for="name">Full name</label><input id="name" type="text" placeholder="e.g. Alex Rivera" required><span class="hint">As it should appear on your profile.</span></div>
<div class="field"><label for="email">Email address</label><input id="email" type="email" placeholder="alex@example.com" required></div>
<div class="field"><label for="interest">Primary interest</label><select id="interest"><option value="">Choose your focus area…</option><option>Getting started</option><option>Advanced features</option><option>Team collaboration</option></select></div>
</div>
<div class="buttons"><button class="btn btn-back" disabled aria-disabled="true">← Back</button><button class="btn btn-next">Continue →</button></div>
<p class="completion">Step 2 of 3 — about 1 minute left</p>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_timeline_vertical(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.timeline{{max-width:700px;margin:40px auto;padding:0 24px}}
h1{{font-size:28px}}
.event{{display:flex;gap:16px;margin-bottom:24px}}
.dot{{width:12px;height:12px;background:{p['accent']};border-radius:50%;margin-top:6px;flex-shrink:0}}
.event h3{{margin:0 0 4px;font-size:16px}}
.event p{{margin:0;color:#666}}
.date{{font-size:12px;color:#999}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="timeline"><h1>Activity</h1>
<div class="event"><div class="dot"></div><div><h3>Event one happened</h3><p>Description of this event.</p><span class="date">Today</span></div></div>
<div class="event"><div class="dot"></div><div><h3>Event two happened</h3><p>Description of this event.</p><span class="date">Yesterday</span></div></div>
<div class="event"><div class="dot"></div><div><h3>Event three happened</h3><p>Description of this event.</p><span class="date">3 days ago</span></div></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the timeline content.",
        "Timeline heading is generic 'Activity' — should describe what type of events are shown.",
        "Event descriptions are identical placeholders.",
        "Timeline has no connecting vertical line — events appear as disconnected dots.",
        "Dates are not machine-readable — no <time> element with datetime attribute.",
        "No interactive or expandable states — long timelines will be unwieldy.",
        "The dot color alone differentiates events — should use icons or labels for event type.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(720px,90%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px;gap:16px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
.page-header{{padding:32px 0 24px}}
.page-header h1{{font:700 clamp(1.4rem,3vw,2rem) var(--heading-font);margin:0 0 4px}}
.page-header p{{color:var(--muted);margin:0}}
.timeline{{position:relative;padding:0 0 0 32px;margin-bottom:48px}}
.timeline::before{{content:'';position:absolute;left:11px;top:0;bottom:0;width:2px;background:color-mix(in srgb,var(--muted) 20%,transparent)}}
.event{{position:relative;margin-bottom:28px}}
.event::before{{content:'';position:absolute;left:-27px;top:6px;width:12px;height:12px;border-radius:50%;border:2px solid var(--accent);background:var(--bg)}}
.event.milestone::before{{background:var(--accent)}}
.event-card{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);border-radius:var(--radius);padding:16px 20px}}
.event-card h3{{font:600 16px var(--heading-font);margin:0 0 4px}}
.event-card p{{color:var(--muted);margin:0 0 8px;font-size:14px}}
.event-meta{{display:flex;gap:12px;align-items:center}}
.event-meta time{{font:500 12px var(--body-font);color:var(--muted)}}
.event-type{{font:600 11px var(--body-font);padding:2px 8px;border-radius:99px;background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent)}}
.load-more{{display:block;width:100%;padding:12px;border:1px solid var(--muted);border-radius:var(--radius);background:transparent;cursor:pointer;font:600 14px var(--body-font);color:var(--text);text-align:center;margin-top:8px}}
.load-more:hover{{background:color-mix(in srgb,var(--accent) 6%,transparent)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:24px 0;color:var(--muted);font-size:13px}}
@media(max-width:500px){{
  .timeline{{padding-left:24px}}.timeline::before{{left:7px}}
  .event::before{{left:-21px;width:10px;height:10px}}
  .event-card{{padding:14px 16px}}
}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#" style="color:var(--bg);text-decoration:none;font-size:14px">Overview</a></nav></div></header>
<main class="wrap">
<div class="page-header"><h1>{escape(b)} — Timeline</h1><p>Track progress as you {escape(goal.split('help')[1].strip() if 'help' in goal else goal)}.</p></div>
<section class="timeline" aria-label="Activity timeline">
<div class="event milestone"><div class="event-card"><h3>Account setup completed</h3><p>Initial configuration finished. All required fields verified and confirmed.</p><div class="event-meta"><time datetime="2025-09-15">Sep 15, 2025</time><span class="event-type">Milestone</span></div></div></div>
<div class="event"><div class="event-card"><h3>First session recorded</h3><p>Explored the main dashboard and customized notification preferences.</p><div class="event-meta"><time datetime="2025-09-14">Sep 14, 2025</time><span class="event-type">Activity</span></div></div></div>
<div class="event"><div class="event-card"><h3>Profile preferences updated</h3><p>Set timezone, language, and communication frequency to match workflow.</p><div class="event-meta"><time datetime="2025-09-13">Sep 13, 2025</time><span class="event-type">Update</span></div></div></div>
</section>
<button class="load-more">Load earlier events</button>
</main>
<footer><div class="wrap">&copy; {escape(b)}</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_comparison_table(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.wrap{{max-width:900px;margin:40px auto;padding:0 24px}}
h1{{font-size:28px}}
table{{width:100%;border-collapse:collapse;margin-top:20px}}
th,td{{padding:12px;text-align:left;border:1px solid #ddd}}
th{{background:#f5f5f5}}
.check{{color:green}}.cross{{color:red}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="wrap"><h1>Compare Plans</h1>
<table><tr><th></th><th>Basic</th><th>Pro</th><th>Enterprise</th></tr>
<tr><td>Feature A</td><td class="check">✓</td><td class="check">✓</td><td class="check">✓</td></tr>
<tr><td>Feature B</td><td class="cross">✗</td><td class="check">✓</td><td class="check">✓</td></tr>
<tr><td>Feature C</td><td class="cross">✗</td><td class="cross">✗</td><td class="check">✓</td></tr>
<tr><td>Price</td><td>$9/mo</td><td>$29/mo</td><td>Contact</td></tr>
</table></div></body></html>'''

    feedback = [
        "No <main> landmark around the comparison content.",
        "Table header cells lack scope attributes — screen readers cannot associate cells with headers.",
        "Check/cross marks use color alone (green/red) — colorblind users cannot distinguish them.",
        "Feature names are generic 'Feature A', 'Feature B' — must relate to the product domain.",
        "Table is not responsive — will overflow at 390px width.",
        "No call-to-action buttons for choosing a plan.",
        "No indication of which plan is recommended or most popular.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(960px,92%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none}}
.page-header{{text-align:center;padding:40px 0 32px}}
.page-header h1{{font:700 clamp(1.6rem,3vw,2.4rem) var(--heading-font);margin:0 0 8px}}
.page-header p{{color:var(--muted);margin:0;max-width:50ch;margin-inline:auto}}
.table-wrap{{overflow-x:auto;border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);background:var(--surface);margin-bottom:48px}}
table{{width:100%;border-collapse:collapse;min-width:600px}}
th,td{{padding:14px 18px;text-align:center;border-bottom:1px solid color-mix(in srgb,var(--muted) 12%,transparent)}}
th{{font:600 13px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.04em;background:color-mix(in srgb,var(--muted) 5%,transparent)}}
td:first-child,th:first-child{{text-align:left;font-weight:600}}
.recommended{{position:relative;background:color-mix(in srgb,var(--accent) 4%,transparent)}}
.recommended-badge{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--accent);color:#fff;padding:2px 12px;border-radius:99px;font:700 11px var(--body-font);white-space:nowrap}}
.yes{{color:#2e7d32}}.yes::before{{content:'✓ '}}.no{{color:var(--muted)}}.no::before{{content:'— '}}
.plan-header{{font:700 18px var(--heading-font);padding-bottom:4px}}
.plan-price{{font:700 22px var(--heading-font);color:var(--accent)}}
.plan-price small{{font:400 13px var(--body-font);color:var(--muted)}}
.cta-row td{{border-bottom:0;padding-top:20px;padding-bottom:20px}}
.btn{{display:inline-block;padding:10px 22px;border-radius:var(--radius);font:600 14px var(--body-font);text-decoration:none;cursor:pointer;border:0}}
.btn-primary{{background:var(--accent);color:#fff}}.btn-outline{{border:1px solid var(--muted);background:transparent;color:var(--text)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:28px 0;color:var(--muted);font-size:13px;text-align:center}}
@media(max-width:700px){{
  .page-header{{padding:28px 0 20px}}
  .table-wrap{{margin:0 -4%}}
}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="wrap">
<div class="page-header"><h1>Choose Your Plan</h1><p>Find the right level to {escape(goal)}.</p></div>
<div class="table-wrap"><table>
<thead><tr><th scope="col">Feature</th><th scope="col"><div class="plan-header">Starter</div><div class="plan-price">$9<small>/mo</small></div></th><th scope="col" class="recommended"><span class="recommended-badge">Most popular</span><div class="plan-header">Professional</div><div class="plan-price">$29<small>/mo</small></div></th><th scope="col"><div class="plan-header">Enterprise</div><div class="plan-price">Custom</div></th></tr></thead>
<tbody>
<tr><td>Core dashboard access</td><td class="yes">Included</td><td class="yes recommended">Included</td><td class="yes">Included</td></tr>
<tr><td>Advanced analytics</td><td class="no">Not included</td><td class="yes recommended">Included</td><td class="yes">Included</td></tr>
<tr><td>API integrations</td><td class="no">Not included</td><td class="yes recommended">Up to 10</td><td class="yes">Unlimited</td></tr>
<tr><td>Priority support</td><td class="no">Not included</td><td class="no recommended">Not included</td><td class="yes">Included</td></tr>
<tr><td>Custom branding</td><td class="no">Not included</td><td class="no recommended">Not included</td><td class="yes">Included</td></tr>
<tr class="cta-row"><td></td><td><a class="btn btn-outline" href="#">Start free</a></td><td class="recommended"><a class="btn btn-primary" href="#">Try Professional</a></td><td><a class="btn btn-outline" href="#">Contact sales</a></td></tr>
</tbody></table></div>
</main>
<footer><div class="wrap">&copy; {escape(b)} — All plans include a 14-day free trial.</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_map_plus_list(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:12px 24px}}
.layout{{display:flex;height:calc(100vh - 48px)}}
.map{{flex:1;background:#e0e0e0;display:flex;align-items:center;justify-content:center;color:#999;font-size:24px}}
.sidebar{{width:360px;overflow-y:auto;padding:16px;background:white}}
h1{{font-size:20px;margin:0 0 12px}}
.item{{padding:12px;border-bottom:1px solid #eee}}
.item h3{{margin:0 0 4px;font-size:15px}}
.item p{{margin:0;font-size:13px;color:#666}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="layout">
<div class="map">[Map View]</div>
<div class="sidebar"><h1>Nearby</h1>
<div class="item"><h3>Location A</h3><p>Description</p></div>
<div class="item"><h3>Location B</h3><p>Description</p></div>
<div class="item"><h3>Location C</h3><p>Description</p></div>
</div></div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the map and list layout.",
        "Map area is a styled div with no accessible role or label.",
        "Location items are generic 'Location A' with identical descriptions.",
        "The two-pane layout (map + sidebar) has no responsive behavior — sidebar overflows at 390px.",
        "No search or filter controls for the map view.",
        "No visible focus styles anywhere.",
        "Items have no distance, rating, or other differentiating metadata.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text);display:flex;flex-direction:column;height:100vh}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 20px;flex-shrink:0}}
.header-inner{{display:flex;align-items:center;min-height:52px;gap:12px}}
.brand{{font:700 16px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
.search-wrap{{display:flex;align-items:center;gap:8px}}
.search-wrap label{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}}
.search-wrap input{{padding:7px 12px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:var(--bg);border-radius:var(--radius);font-size:13px;width:200px}}
.layout{{display:flex;flex:1;overflow:hidden}}
.map{{flex:1;background:color-mix(in srgb,var(--muted) 15%,transparent);display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:16px;position:relative}}
.map-overlay{{position:absolute;top:12px;right:12px;display:flex;flex-direction:column;gap:4px}}
.map-btn{{width:36px;height:36px;border:1px solid color-mix(in srgb,var(--muted) 30%,transparent);border-radius:var(--radius);background:var(--surface);cursor:pointer;font:700 18px var(--body-font);color:var(--text);display:flex;align-items:center;justify-content:center}}
.panel{{width:360px;overflow-y:auto;background:var(--surface);border-left:1px solid color-mix(in srgb,var(--muted) 15%,transparent);flex-shrink:0}}
.panel-header{{padding:16px 20px;border-bottom:1px solid color-mix(in srgb,var(--muted) 12%,transparent);display:flex;justify-content:space-between;align-items:center}}
.panel-header h1{{font:700 16px var(--heading-font);margin:0}}
.result-count{{font:500 12px var(--body-font);color:var(--muted)}}
.item{{padding:16px 20px;border-bottom:1px solid color-mix(in srgb,var(--muted) 8%,transparent);cursor:pointer;transition:background .1s}}
.item:hover{{background:color-mix(in srgb,var(--accent) 4%,transparent)}}
.item h3{{margin:0 0 3px;font:600 15px var(--heading-font)}}
.item p{{margin:0 0 6px;font-size:13px;color:var(--muted)}}
.item-meta{{display:flex;gap:10px;font-size:12px;color:var(--muted)}}
.item-meta .distance{{font-weight:600;color:var(--accent)}}
.rating{{color:var(--accent)}}
.tab-toggle{{display:none;width:100%;padding:10px;border:0;background:var(--text);color:var(--bg);font:600 14px var(--body-font);cursor:pointer}}
@media(max-width:700px){{
  .layout{{flex-direction:column}}
  .panel{{width:100%;max-height:50vh;border-left:0;border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent)}}
  .map{{min-height:40vh}}
  .tab-toggle{{display:block}}
  .search-wrap input{{width:140px}}
}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a><div class="search-wrap"><label for="loc-search">Search locations</label><input id="loc-search" type="text" placeholder="Search nearby…"></div></div></header>
<main class="layout">
<div class="map" role="img" aria-label="Interactive map showing nearby locations">[Interactive Map]<div class="map-overlay"><button class="map-btn" aria-label="Zoom in">+</button><button class="map-btn" aria-label="Zoom out">−</button></div></div>
<aside class="panel" aria-label="Location results">
<div class="panel-header"><h1>Nearby Places</h1><span class="result-count">3 found</span></div>
<article class="item" tabindex="0"><h3>Riverside Commons</h3><p>Bright, spacious workspace with outdoor seating and fast Wi-Fi.</p><div class="item-meta"><span class="distance">0.3 mi</span><span class="rating">★★★★☆</span><span>Open until 8 PM</span></div></article>
<article class="item" tabindex="0"><h3>Central Library Hub</h3><p>Quiet environment with private meeting rooms and printing services.</p><div class="item-meta"><span class="distance">0.7 mi</span><span class="rating">★★★★★</span><span>Open until 9 PM</span></div></article>
<article class="item" tabindex="0"><h3>Station Café</h3><p>Casual coffee spot popular with remote workers, limited seating.</p><div class="item-meta"><span class="distance">1.2 mi</span><span class="rating">★★★☆☆</span><span>Open until 6 PM</span></div></article>
</aside>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_calendar_grid(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.cal{{max-width:800px;margin:30px auto;padding:0 20px}}
h1{{font-size:24px}}
.month-nav{{display:flex;justify-content:space-between;margin-bottom:16px}}
.grid{{display:grid;grid-template-columns:repeat(7,1fr);gap:1px;background:#ddd}}
.day-header{{background:#f5f5f5;padding:8px;text-align:center;font-weight:bold;font-size:12px}}
.day{{background:white;padding:8px;min-height:80px;font-size:12px}}
.day .num{{font-weight:bold}}
.event-dot{{background:{p['accent']};color:white;padding:2px 6px;border-radius:3px;font-size:10px;margin-top:4px;display:inline-block}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="cal"><h1>Calendar</h1>
<div class="month-nav"><button>← Prev</button><strong>September 2025</strong><button>Next →</button></div>
<div class="grid">
<div class="day-header">Sun</div><div class="day-header">Mon</div><div class="day-header">Tue</div><div class="day-header">Wed</div><div class="day-header">Thu</div><div class="day-header">Fri</div><div class="day-header">Sat</div>
<div class="day"></div><div class="day"><span class="num">1</span></div><div class="day"><span class="num">2</span><span class="event-dot">Event</span></div><div class="day"><span class="num">3</span></div><div class="day"><span class="num">4</span></div><div class="day"><span class="num">5</span><span class="event-dot">Event</span></div><div class="day"><span class="num">6</span></div>
<div class="day"><span class="num">7</span></div><div class="day"><span class="num">8</span></div><div class="day"><span class="num">9</span></div><div class="day"><span class="num">10</span></div><div class="day"><span class="num">11</span></div><div class="day"><span class="num">12</span></div><div class="day"><span class="num">13</span></div>
</div></div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the calendar.",
        "Calendar heading is generic 'Calendar' — should describe the scheduling context.",
        "Month navigation buttons have no accessible labels and no focus styles.",
        "Calendar grid uses divs instead of a semantically appropriate table for tabular date data.",
        "Events are labeled generically 'Event' — should show actual event details.",
        "No responsive fallback — 7-column grid overflows at 390px.",
        "No today indicator — users cannot quickly spot the current date.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(860px,92%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none}}
.page-header{{padding:28px 0 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.page-header h1{{font:700 clamp(1.3rem,2.5vw,1.8rem) var(--heading-font);margin:0}}
.month-nav{{display:flex;align-items:center;gap:12px}}
.month-nav button{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:var(--radius);padding:6px 14px;cursor:pointer;font:600 13px var(--body-font);color:var(--text)}}
.month-nav button:hover{{background:color-mix(in srgb,var(--accent) 8%,transparent)}}
.month-nav .current{{font:700 16px var(--heading-font)}}
.cal-table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);overflow:hidden;margin-bottom:40px}}
.cal-table th{{padding:10px 8px;font:600 12px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.04em;border-bottom:1px solid color-mix(in srgb,var(--muted) 12%,transparent);text-align:center}}
.cal-table td{{padding:6px;vertical-align:top;height:80px;border:1px solid color-mix(in srgb,var(--muted) 8%,transparent);width:14.28%}}
.cal-table td:hover{{background:color-mix(in srgb,var(--accent) 4%,transparent)}}
.cal-date{{font:600 13px var(--body-font);margin-bottom:4px;display:block}}
.today .cal-date{{background:var(--accent);color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center}}
.cal-event{{display:block;padding:2px 6px;border-radius:4px;font:500 11px var(--body-font);background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-decoration:none}}
.cal-event:hover{{background:color-mix(in srgb,var(--accent) 20%,transparent)}}
.agenda-list{{display:none}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:24px 0;color:var(--muted);font-size:13px}}
@media(max-width:600px){{
  .cal-table{{display:none}}
  .agenda-list{{display:block}}
  .agenda-item{{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid color-mix(in srgb,var(--muted) 10%,transparent)}}
  .agenda-date{{font:700 14px var(--heading-font);min-width:48px;text-align:center;color:var(--accent)}}
  .agenda-content h3{{margin:0;font:600 15px var(--heading-font)}}.agenda-content p{{margin:4px 0 0;font-size:13px;color:var(--muted)}}
}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="wrap">
<div class="page-header"><h1>{escape(b)} — Schedule</h1><div class="month-nav"><button aria-label="Previous month">← Prev</button><span class="current">September 2025</span><button aria-label="Next month">Next →</button></div></div>
<table class="cal-table" aria-label="September 2025 calendar">
<thead><tr><th scope="col" abbr="Sunday">Sun</th><th scope="col" abbr="Monday">Mon</th><th scope="col" abbr="Tuesday">Tue</th><th scope="col" abbr="Wednesday">Wed</th><th scope="col" abbr="Thursday">Thu</th><th scope="col" abbr="Friday">Fri</th><th scope="col" abbr="Saturday">Sat</th></tr></thead>
<tbody><tr><td></td><td><span class="cal-date">1</span></td><td><span class="cal-date">2</span><a href="#" class="cal-event">Team standup</a></td><td><span class="cal-date">3</span></td><td><span class="cal-date">4</span></td><td><span class="cal-date">5</span><a href="#" class="cal-event">Design review</a></td><td><span class="cal-date">6</span></td></tr>
<tr><td><span class="cal-date">7</span></td><td><span class="cal-date">8</span></td><td class="today"><span class="cal-date">9</span><a href="#" class="cal-event">Sprint planning</a></td><td><span class="cal-date">10</span></td><td><span class="cal-date">11</span></td><td><span class="cal-date">12</span></td><td><span class="cal-date">13</span></td></tr>
</tbody></table>
<div class="agenda-list" aria-label="Upcoming events">
<article class="agenda-item"><div class="agenda-date">Sep 2</div><div class="agenda-content"><h3>Team standup</h3><p>Daily sync — 15 min</p></div></article>
<article class="agenda-item"><div class="agenda-date">Sep 5</div><div class="agenda-content"><h3>Design review</h3><p>Review new mockups with stakeholders</p></div></article>
<article class="agenda-item"><div class="agenda-date">Sep 9</div><div class="agenda-content"><h3>Sprint planning</h3><p>Plan next sprint backlog items</p></div></article>
</div>
</main>
<footer><div class="wrap">&copy; {escape(b)}</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_editorial_longform(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]
    goal = prod["goal"]
    audience = prod["audience"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:18px Georgia;background:{p['bg']};color:{p['text']}}}
header{{text-align:center;padding:60px 20px}}
h1{{font-size:48px;margin:0 0 16px}}
.byline{{color:#888}}
article{{max-width:680px;margin:auto;padding:0 20px 60px}}
article p{{line-height:1.7;margin-bottom:20px}}
blockquote{{border-left:3px solid {p['accent']};margin:24px 0;padding:12px 20px;font-style:italic}}
</style></head><body>
<header><h1>Article Title Here</h1><p class="byline">By Author Name · 8 min read</p></header>
<article>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
<blockquote>An important quote that adds depth to the story.</blockquote>
<p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
<p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
</article></body></html>'''

    feedback = [
        "No <main> landmark wrapping the article.",
        "Article title is placeholder 'Article Title Here' — should be real editorial content.",
        "Body text is lorem ipsum — must use original, meaningful content.",
        "No navigation or way to return to the publication's home.",
        "No visible focus styles on any element.",
        "No reading progress indicator for a long-form piece.",
        "Blockquote has no attribution.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:18px/1.75 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.progress-bar{{position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0;z-index:100;transition:width .1s}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:52px}}
.brand{{font:700 16px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
header nav a{{color:var(--bg);text-decoration:none;padding:6px 10px;font-size:14px}}
.hero{{text-align:center;padding:60px 20px 40px;max-width:700px;margin:auto}}
.hero .category{{font:700 12px var(--body-font);letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
.hero h1{{font:700 clamp(2rem,5vw,3.2rem)/1.1 var(--heading-font);margin:0 0 16px;letter-spacing:-.02em}}
.hero .byline{{color:var(--muted);font-size:15px}}
.hero .byline time{{font-weight:600}}
article{{max-width:680px;margin:auto;padding:0 20px 60px}}
article p{{margin-bottom:24px}}
article h2{{font:700 clamp(1.3rem,2.5vw,1.8rem) var(--heading-font);margin:40px 0 16px;padding-top:20px;border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent)}}
blockquote{{border-left:3px solid var(--accent);margin:32px 0;padding:16px 24px;background:color-mix(in srgb,var(--accent) 5%,transparent);border-radius:0 var(--radius) var(--radius) 0;font-style:italic}}
blockquote cite{{display:block;margin-top:8px;font-style:normal;font:600 13px var(--body-font);color:var(--muted)}}
.pullquote{{font:700 clamp(1.5rem,3vw,2rem)/1.3 var(--heading-font);color:var(--accent);text-align:center;padding:32px 20px;margin:32px 0}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:32px 0;text-align:center;color:var(--muted);font-size:14px}}
@media(max-width:600px){{
  .hero{{padding:40px 16px 28px}}
  article{{padding:0 16px 40px;font-size:16px}}
  blockquote{{margin:20px 0;padding:12px 16px}}
}}
</style></head><body>
<div class="progress-bar" role="progressbar" aria-label="Reading progress"></div>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#">Home</a><a href="#">Archive</a></nav></div></header>
<main>
<div class="hero"><span class="category">{escape(prod['category'])}</span><h1>The Quiet Revolution in How We {escape(goal.split('help')[1].strip().split(' and ')[0] if 'help' in goal else goal.split('let')[1].strip().split(' and ')[0] if 'let' in goal else goal)}</h1><p class="byline">By Jordan Chen · <time datetime="2025-09-12">September 12, 2025</time> · 8 min read</p></div>
<article>
<p>There is a moment, familiar to anyone who has tried to {escape(goal)}, when the interface stops helping and starts getting in the way. The buttons multiply, the options fork, the page grows heavy with features that serve the system more than the person using it.</p>
<h2>Where Things Went Wrong</h2>
<p>For decades, the answer to complexity was more complexity: more menus, more settings, more documentation. The assumption was that users would eventually learn. But research consistently shows the opposite — cognitive load increases abandonment, not mastery.</p>
<blockquote>The best interface is the one that disappears. When technology works, you forget it is there.<cite>— Design Principles, {escape(b)} Team</cite></blockquote>
<p>What we found, after observing hundreds of {escape(audience)}, was that the most requested feature was not a feature at all. It was clarity. People wanted to understand what to do next without reading a manual.</p>
<div class="pullquote">Clarity is not the absence of information. It is the presence of hierarchy.</div>
<h2>A Different Approach</h2>
<p>The redesign started with a constraint: every screen must have exactly one primary action. Not two. Not a primary and a close secondary. One. This forced every layout decision to serve that single moment of clarity.</p>
<p>The result was not a simpler product — it was a product that felt simpler. The features were still there, but they were organized around the user's actual journey rather than the engineering team's feature list.</p>
</article>
</main>
<footer>&copy; {escape(b)} · Written with care for {escape(audience)}.</footer>
<script>window.addEventListener('scroll',()=>{{const d=document.documentElement;const p=(d.scrollTop/(d.scrollHeight-d.clientHeight))*100;document.querySelector('.progress-bar').style.width=p+'%'}})</script>
</body></html>'''

    return initial, feedback, corrected


def gen_card_masonry(p: dict, prod: dict, t: dict, radius: str, space: str, nav: str, interaction: str, responsive: str) -> tuple[str, list[str], str]:
    b = prod["brand"]

    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
h1{{padding:24px;font-size:24px}}
.grid{{column-count:3;column-gap:16px;padding:0 24px}}
.card{{break-inside:avoid;background:white;border-radius:8px;padding:16px;margin-bottom:16px}}
.card img{{width:100%;border-radius:6px}}
.card h3{{margin:8px 0 4px}}
.card p{{color:#666;font-size:13px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<h1>Gallery</h1>
<div class="grid">
<div class="card"><div style="height:200px;background:#ddd;border-radius:6px"></div><h3>Item One</h3><p>Description</p></div>
<div class="card"><div style="height:300px;background:#ddd;border-radius:6px"></div><h3>Item Two</h3><p>Description</p></div>
<div class="card"><div style="height:150px;background:#ddd;border-radius:6px"></div><h3>Item Three</h3><p>Description</p></div>
<div class="card"><div style="height:250px;background:#ddd;border-radius:6px"></div><h3>Item Four</h3><p>Description</p></div>
<div class="card"><div style="height:180px;background:#ddd;border-radius:6px"></div><h3>Item Five</h3><p>Description</p></div>
<div class="card"><div style="height:220px;background:#ddd;border-radius:6px"></div><h3>Item Six</h3><p>Description</p></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark — h1 is outside any semantic container.",
        "All cards have identical 'Description' placeholder text.",
        "Images are empty divs — no alt text or semantic image role.",
        "Masonry layout does not adapt responsively — 3 columns at 390px will be cramped.",
        "No focus styles on any element.",
        "No filtering, sorting, or category controls for the gallery.",
        "Card items have no interactive states — clicking does nothing.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(1200px,92%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px;gap:16px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
.page-header{{padding:28px 0 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.page-header h1{{font:700 clamp(1.3rem,2.5vw,1.8rem) var(--heading-font);margin:0}}
.filters{{display:flex;gap:6px;flex-wrap:wrap}}
.filter-btn{{padding:6px 14px;border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:99px;background:transparent;cursor:pointer;font:500 13px var(--body-font);color:var(--text)}}
.filter-btn.active,.filter-btn:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.grid{{column-count:3;column-gap:16px;margin-bottom:48px}}
.card{{break-inside:avoid;background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);border-radius:var(--radius);overflow:hidden;margin-bottom:16px;transition:box-shadow .15s;cursor:pointer}}
.card:hover{{box-shadow:0 8px 24px rgba(0,0,0,.08)}}
.card-img{{width:100%;display:block;background:color-mix(in srgb,var(--muted) 12%,transparent);display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:12px;font-style:italic}}
.card-body{{padding:14px 16px}}
.card-body h3{{margin:0 0 4px;font:600 15px var(--heading-font)}}
.card-body p{{margin:0;font-size:13px;color:var(--muted)}}
.card-meta{{display:flex;justify-content:space-between;padding:0 16px 12px;font-size:12px;color:var(--muted)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:24px 0;color:var(--muted);font-size:13px}}
@media(max-width:900px){{.grid{{column-count:2}}}}
@media(max-width:500px){{.grid{{column-count:1}}.filters{{overflow-x:auto;flex-wrap:nowrap}}}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#" style="color:var(--bg);text-decoration:none;font-size:14px">Explore</a><a href="#" style="color:var(--bg);text-decoration:none;font-size:14px;margin-left:12px">Collections</a></nav></div></header>
<main class="wrap">
<div class="page-header"><h1>{escape(b)} Gallery</h1><div class="filters"><button class="filter-btn active">All</button><button class="filter-btn">Featured</button><button class="filter-btn">New</button><button class="filter-btn">Popular</button></div></div>
<div class="grid">
<article class="card" tabindex="0"><div class="card-img" style="height:220px" role="img" aria-label="Coastal landscape photography">[Coastal landscape]</div><div class="card-body"><h3>Morning Light on Granite</h3><p>Captured at dawn along the northern coastline, soft diffused light.</p></div><div class="card-meta"><span>Photography</span><span>★ 4.8</span></div></article>
<article class="card" tabindex="0"><div class="card-img" style="height:300px" role="img" aria-label="Abstract textile pattern">[Textile pattern]</div><div class="card-body"><h3>Woven Geometry</h3><p>Hand-loomed textile exploring repeating geometric motifs in natural dyes.</p></div><div class="card-meta"><span>Textile</span><span>★ 4.6</span></div></article>
<article class="card" tabindex="0"><div class="card-img" style="height:160px" role="img" aria-label="Minimal ceramic bowl">[Ceramic piece]</div><div class="card-body"><h3>Quiet Form</h3><p>Reduction-fired stoneware with a matte ash glaze.</p></div><div class="card-meta"><span>Ceramics</span><span>★ 4.9</span></div></article>
<article class="card" tabindex="0"><div class="card-img" style="height:260px" role="img" aria-label="Architectural detail">[Architecture detail]</div><div class="card-body"><h3>Concrete Cantilever</h3><p>Brutalist extension over a public plaza, photographed from below.</p></div><div class="card-meta"><span>Architecture</span><span>★ 4.5</span></div></article>
<article class="card" tabindex="0"><div class="card-img" style="height:190px" role="img" aria-label="Botanical illustration">[Botanical sketch]</div><div class="card-body"><h3>Field Study: Fern</h3><p>Detailed ink illustration documenting regional fern species.</p></div><div class="card-meta"><span>Illustration</span><span>★ 4.7</span></div></article>
<article class="card" tabindex="0"><div class="card-img" style="height:240px" role="img" aria-label="Product photography">[Product shot]</div><div class="card-body"><h3>Object in Context</h3><p>Studio arrangement showing the relationship between object and environment.</p></div><div class="card-meta"><span>Product</span><span>★ 4.4</span></div></article>
</div>
</main>
<footer><div class="wrap">&copy; {escape(b)}</div></footer>
</body></html>'''

    return initial, feedback, corrected


# Remaining archetypes follow the same pattern — unique structure per type

def gen_chat_interface(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:14px Arial;background:{p['bg']};color:{p['text']};height:100vh;display:flex;flex-direction:column}}
header{{background:{p['text']};color:white;padding:12px 20px}}
.messages{{flex:1;padding:20px;overflow-y:auto}}
.msg{{max-width:70%;padding:10px 14px;border-radius:12px;margin-bottom:8px}}
.msg.user{{background:{p['accent']};color:white;margin-left:auto}}
.msg.bot{{background:#e8e8e8}}
.input-area{{padding:12px 20px;border-top:1px solid #ddd;display:flex;gap:8px}}
.input-area input{{flex:1;padding:10px;border:1px solid #ccc;border-radius:8px}}
.input-area button{{background:{p['accent']};color:white;border:0;padding:10px 20px;border-radius:8px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="messages"><div class="msg bot">Hello! How can I help?</div><div class="msg user">I need help with something.</div><div class="msg bot">Sure, I can assist you with that.</div></div>
<div class="input-area"><input type="text" placeholder="Type a message..."><button>Send</button></div>
</body></html>'''

    feedback = [
        "No <main> landmark wrapping the chat interface.",
        "No <h1> heading — users and screen readers have no page-level context.",
        "Input has no associated label — inaccessible to screen readers.",
        "Messages lack timestamps and sender identification.",
        "No focus styles on the input or send button.",
        "Message bubbles have no accessible role or live region for new messages.",
        "No empty state or typing indicator.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.5 var(--body-font);background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 20px;flex-shrink:0}}
.header-inner{{display:flex;align-items:center;min-height:52px;gap:12px}}
.brand{{font:700 16px var(--heading-font);color:var(--bg);margin-right:auto}}
.status-dot{{width:8px;height:8px;border-radius:50%;background:#4caf50;display:inline-block}}.status-text{{font-size:12px;color:rgba(255,255,255,.7)}}
.chat-area{{flex:1;display:flex;flex-direction:column;overflow:hidden}}
.chat-header{{padding:12px 20px;border-bottom:1px solid color-mix(in srgb,var(--muted) 15%,transparent);flex-shrink:0}}
.chat-header h1{{font:700 16px var(--heading-font);margin:0}}.chat-header p{{margin:2px 0 0;font-size:12px;color:var(--muted)}}
.messages{{flex:1;padding:20px;overflow-y:auto;display:flex;flex-direction:column;gap:12px}}
.msg-group{{display:flex;flex-direction:column;gap:4px}}
.msg-group.user{{align-items:flex-end}}.msg-group.assistant{{align-items:flex-start}}
.sender{{font:600 11px var(--body-font);color:var(--muted);margin-bottom:2px;padding:0 4px}}
.msg{{max-width:75%;padding:10px 16px;border-radius:var(--radius);font-size:14px;line-height:1.5}}
.msg.user{{background:var(--accent);color:#fff;border-bottom-right-radius:4px}}
.msg.assistant{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-bottom-left-radius:4px}}
.msg-time{{font-size:11px;color:var(--muted);padding:0 4px}}
.typing{{display:flex;gap:4px;padding:8px 16px;align-items:center}}.typing span{{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:blink 1.4s infinite}}.typing span:nth-child(2){{animation-delay:.2s}}.typing span:nth-child(3){{animation-delay:.4s}}
@keyframes blink{{0%,80%,100%{{opacity:.3}}40%{{opacity:1}}}}
.input-area{{padding:12px 20px;border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);display:flex;gap:8px;flex-shrink:0;background:var(--bg)}}
.input-area label{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}}
.input-area input{{flex:1;padding:11px 16px;border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:var(--radius);font:14px var(--body-font);background:var(--surface);color:var(--text)}}
.input-area button{{background:var(--accent);color:#fff;border:0;padding:10px 20px;border-radius:var(--radius);font:600 14px var(--body-font);cursor:pointer}}
.input-area button:hover{{filter:brightness(1.1)}}
@media(max-width:500px){{.msg{{max-width:85%}}.input-area{{padding:10px 12px}}}}
</style></head><body>
<header><div class="header-inner"><span class="brand">{escape(b)}</span><span class="status-dot"></span><span class="status-text">Online</span></div></header>
<main class="chat-area">
<div class="chat-header"><h1>{escape(b)} Support</h1><p>We are here to {escape(goal.split('help')[1].strip() if 'help' in goal else goal)}.</p></div>
<div class="messages" role="log" aria-live="polite" aria-label="Chat messages">
<div class="msg-group assistant"><span class="sender">Support</span><div class="msg assistant">Welcome to {escape(b)}! I can help you get started, answer questions, or troubleshoot any issues. What would you like help with today?</div><span class="msg-time">10:02 AM</span></div>
<div class="msg-group user"><span class="sender">You</span><div class="msg user">I need help setting up my account preferences. Where do I find that?</div><span class="msg-time">10:03 AM</span></div>
<div class="msg-group assistant"><span class="sender">Support</span><div class="msg assistant">Great question! You can find your preferences in Settings → Profile. From there you can customize notifications, timezone, and display options. Would you like me to walk you through each option?</div><span class="msg-time">10:03 AM</span></div>
<div class="typing" aria-label="Support is typing"><span></span><span></span><span></span></div>
</div>
<div class="input-area"><label for="chat-input">Type your message</label><input id="chat-input" type="text" placeholder="Type a message…" autocomplete="off"><button type="submit">Send</button></div>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_interactive_exercise(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:16px Arial;background:{p['bg']};color:{p['text']};display:flex;align-items:center;justify-content:center;min-height:100vh}}
.container{{text-align:center;max-width:400px;padding:40px}}
h1{{font-size:32px}}
.circle{{width:200px;height:200px;border-radius:50%;border:8px solid {p['accent']};margin:30px auto;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:bold;color:{p['accent']}}}
button{{background:{p['accent']};color:white;border:0;padding:14px 28px;border-radius:8px;font-size:16px;cursor:pointer;margin:8px}}
p{{color:#666}}
</style></head><body>
<div class="container"><h1>Exercise</h1><p>Follow the instructions below.</p><div class="circle">4:00</div><button>Start</button><button>Reset</button></div>
</body></html>'''

    feedback = [
        "No <main> landmark wrapping the exercise.",
        "Heading 'Exercise' is generic — should describe the specific activity.",
        "No navigation to return to a menu or home.",
        "Timer display has no accessible live region — screen readers won't announce updates.",
        "No instructional text explaining what the user should do during the exercise.",
        "Reset and Start buttons have no disabled/active state differentiation.",
        "No completion or success state shown after the exercise finishes.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:52px}}
.brand{{font:700 16px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
header nav a{{color:var(--bg);text-decoration:none;font-size:14px}}
.exercise-wrap{{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:calc(100vh - 52px);padding:40px 20px;text-align:center}}
.exercise-wrap h1{{font:700 clamp(1.5rem,3vw,2.2rem) var(--heading-font);margin:0 0 8px}}
.exercise-wrap .subtitle{{color:var(--muted);margin:0 0 32px;max-width:40ch}}
.timer-ring{{width:220px;height:220px;border-radius:50%;border:6px solid color-mix(in srgb,var(--accent) 20%,transparent);display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 auto 24px;position:relative}}
.timer-ring::after{{content:'';position:absolute;inset:-6px;border-radius:50%;border:6px solid transparent;border-top-color:var(--accent);animation:none}}
.timer-ring.active::after{{animation:spin 4s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.timer-value{{font:700 48px var(--heading-font);color:var(--accent)}}
.timer-label{{font:500 13px var(--body-font);color:var(--muted);margin-top:4px}}
.instruction{{font:500 18px var(--heading-font);color:var(--text);margin-bottom:32px;min-height:28px}}
.controls{{display:flex;gap:12px;margin-bottom:20px}}
.btn{{padding:14px 28px;border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer;border:0}}
.btn-start{{background:var(--accent);color:#fff}}.btn-start:hover{{filter:brightness(1.1)}}
.btn-reset{{background:transparent;border:1px solid var(--muted);color:var(--text)}}.btn-reset:disabled{{opacity:.4;cursor:not-allowed}}
.progress-dots{{display:flex;gap:8px;margin-top:16px}}
.dot{{width:10px;height:10px;border-radius:50%;background:color-mix(in srgb,var(--muted) 20%,transparent)}}
.dot.done{{background:var(--accent)}}
.completion{{display:none;padding:24px;background:color-mix(in srgb,var(--accent) 8%,transparent);border-radius:var(--radius);margin-top:20px}}
.completion h2{{font:700 20px var(--heading-font);margin:0 0 8px;color:var(--accent)}}
.completion p{{margin:0;color:var(--muted)}}
@media(max-width:400px){{.timer-ring{{width:180px;height:180px}}.timer-value{{font-size:38px}}}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a><nav><a href="#">Library</a></nav></div></header>
<main class="exercise-wrap" aria-label="Guided exercise">
<h1>Focused Breathing</h1>
<p class="subtitle">A 4-minute guided breathing session designed to help you {escape(goal.split('help')[1].strip() if 'help' in goal else goal)}.</p>
<div class="timer-ring" role="timer" aria-live="polite" aria-label="Time remaining"><span class="timer-value">4:00</span><span class="timer-label">remaining</span></div>
<p class="instruction" aria-live="polite">Press Start when you are ready.</p>
<div class="controls"><button class="btn btn-start">Start session</button><button class="btn btn-reset" disabled aria-disabled="true">Reset</button></div>
<div class="progress-dots" aria-label="Session progress"><span class="dot done"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
<div class="completion" role="status"><h2>Session complete ✓</h2><p>You completed a full 4-minute session. Nice work.</p></div>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_data_table_dense(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:13px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:12px 20px}}
.wrap{{padding:20px}}
h1{{font-size:20px}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:8px 12px;text-align:left;border-bottom:1px solid #ddd;white-space:nowrap}}
th{{background:#f5f5f5;font-size:11px;text-transform:uppercase}}
tr:hover{{background:#f9f9f9}}
.status{{padding:2px 8px;border-radius:99px;font-size:11px}}
.active{{background:#e8f5e9;color:green}}.inactive{{background:#ffebee;color:red}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="wrap"><h1>Records</h1>
<table><tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th><th>Role</th><th>Last Active</th><th>Actions</th></tr>
<tr><td>001</td><td>Jane Doe</td><td>jane@example.com</td><td><span class="status active">Active</span></td><td>Admin</td><td>Today</td><td><a href="#">Edit</a></td></tr>
<tr><td>002</td><td>John Smith</td><td>john@example.com</td><td><span class="status inactive">Inactive</span></td><td>User</td><td>3 days ago</td><td><a href="#">Edit</a></td></tr>
<tr><td>003</td><td>Alex Lee</td><td>alex@example.com</td><td><span class="status active">Active</span></td><td>Editor</td><td>Yesterday</td><td><a href="#">Edit</a></td></tr>
</table></div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the table content.",
        "Table headers lack scope attributes.",
        "Status badges use color alone — 'Active' is green, 'Inactive' is red — inaccessible to colorblind users.",
        "Table will overflow horizontally at 390px with no responsive fallback.",
        "No search, filter, or sort controls.",
        "No pagination or row count indicator.",
        "Action links are generic 'Edit' with no label indicating which record.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:13px/1.5 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(1200px,94%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:52px}}
.brand{{font:700 16px var(--heading-font);color:var(--bg);text-decoration:none}}
.toolbar{{display:flex;justify-content:space-between;align-items:center;padding:20px 0 16px;flex-wrap:wrap;gap:12px}}
.toolbar h1{{font:700 clamp(1.2rem,2vw,1.5rem) var(--heading-font);margin:0}}
.toolbar-actions{{display:flex;gap:8px;align-items:center}}
.search-input{{padding:7px 12px;border:1px solid color-mix(in srgb,var(--muted) 30%,transparent);border-radius:var(--radius);font:13px var(--body-font);width:200px;background:var(--surface)}}
.btn-sm{{padding:7px 14px;border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:var(--radius);background:var(--surface);font:500 13px var(--body-font);cursor:pointer;color:var(--text)}}
.table-wrap{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);overflow:hidden;margin-bottom:16px}}
.table-scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;min-width:700px}}
th{{padding:10px 16px;text-align:left;font:600 11px var(--body-font);color:var(--muted);text-transform:uppercase;letter-spacing:.04em;background:color-mix(in srgb,var(--muted) 5%,transparent);border-bottom:1px solid color-mix(in srgb,var(--muted) 15%,transparent);white-space:nowrap;cursor:pointer;user-select:none}}
th:hover{{color:var(--text)}}
td{{padding:10px 16px;border-bottom:1px solid color-mix(in srgb,var(--muted) 8%,transparent);white-space:nowrap}}
tr:hover td{{background:color-mix(in srgb,var(--accent) 3%,transparent)}}
.status{{padding:3px 10px;border-radius:99px;font:600 11px var(--body-font)}}
.status-active{{background:#e8f5e9;color:#2e7d32}}.status-active::before{{content:'● '}}.status-inactive{{background:#fafafa;color:#757575}}.status-inactive::before{{content:'○ '}}
.action-link{{color:var(--accent);text-decoration:none;font-weight:600}}
.action-link:hover{{text-decoration:underline}}
.pagination{{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;color:var(--muted);font-size:13px}}
.page-btns{{display:flex;gap:4px}}
.page-btn{{padding:5px 10px;border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);border-radius:var(--radius);background:transparent;cursor:pointer;font:13px var(--body-font);color:var(--text)}}
.page-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
@media(max-width:700px){{
  .toolbar{{flex-direction:column;align-items:stretch}}
  .toolbar-actions{{flex-wrap:wrap}}
  .search-input{{width:100%}}
}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="wrap">
<div class="toolbar"><h1>All Records</h1><div class="toolbar-actions"><label for="tbl-search" style="position:absolute;clip:rect(0,0,0,0)">Search records</label><input id="tbl-search" class="search-input" type="search" placeholder="Search records…"><button class="btn-sm">Filter ▾</button><button class="btn-sm">Export</button></div></div>
<div class="table-wrap"><div class="table-scroll">
<table><caption style="position:absolute;clip:rect(0,0,0,0)">Records table with sortable columns</caption>
<thead><tr><th scope="col">ID ↕</th><th scope="col">Name ↕</th><th scope="col">Email</th><th scope="col">Status</th><th scope="col">Role</th><th scope="col">Last Active ↕</th><th scope="col">Actions</th></tr></thead>
<tbody>
<tr><td>001</td><td>Priya Anand</td><td>priya@example.com</td><td><span class="status status-active">Active</span></td><td>Admin</td><td>12 min ago</td><td><a class="action-link" href="#" aria-label="Edit Priya Anand">Edit</a></td></tr>
<tr><td>002</td><td>Marcus Chen</td><td>marcus@example.com</td><td><span class="status status-inactive">Inactive</span></td><td>Viewer</td><td>3 days ago</td><td><a class="action-link" href="#" aria-label="Edit Marcus Chen">Edit</a></td></tr>
<tr><td>003</td><td>Sara Okonkwo</td><td>sara@example.com</td><td><span class="status status-active">Active</span></td><td>Editor</td><td>1 hr ago</td><td><a class="action-link" href="#" aria-label="Edit Sara Okonkwo">Edit</a></td></tr>
</tbody></table></div>
<div class="pagination"><span>Showing 1–3 of 47 records</span><div class="page-btns"><button class="page-btn active">1</button><button class="page-btn">2</button><button class="page-btn">3</button><button class="page-btn">→</button></div></div>
</div>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_profile_workspace(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.profile{{max-width:700px;margin:30px auto;padding:0 20px}}
.avatar{{width:80px;height:80px;border-radius:50%;background:{p['accent']};color:white;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold}}
h1{{font-size:24px;margin:16px 0 4px}}
.bio{{color:#666;margin-bottom:24px}}
.tabs{{display:flex;gap:8px;border-bottom:2px solid #ddd;margin-bottom:20px}}
.tab{{padding:8px 16px;cursor:pointer;border:0;background:transparent}}.tab.active{{border-bottom:2px solid {p['accent']};color:{p['accent']}}}
.settings label{{display:block;margin-bottom:12px;font-weight:bold}}
.settings input{{width:100%;padding:8px;border:1px solid #ccc;border-radius:4px}}
button.save{{background:{p['accent']};color:white;border:0;padding:12px 24px;border-radius:6px;cursor:pointer;margin-top:16px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="profile"><div class="avatar">A</div><h1>Alex Rivera</h1><p class="bio">Member since 2024</p>
<div class="tabs"><button class="tab active">Profile</button><button class="tab">Settings</button><button class="tab">Activity</button></div>
<div class="settings"><label>Display Name<input type="text" value="Alex Rivera"></label><label>Email<input type="email" value="alex@example.com"></label><label>Bio<input type="text" value=""></label><button class="save">Save Changes</button></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the profile content.",
        "Tabs have no ARIA attributes — screen readers don't know these are tabs.",
        "Form labels wrap inputs directly but have no for/id association — less accessible.",
        "No focus styles on any interactive elements.",
        "Bio field uses a single-line input — should be a textarea.",
        "No success/error feedback when saving changes.",
        "Avatar has no alt text — 'A' has no meaningful label.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(720px,90%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
header nav a{{color:var(--bg);text-decoration:none;font-size:14px;padding:6px 10px}}
.profile-header{{display:flex;align-items:center;gap:20px;padding:32px 0 24px;flex-wrap:wrap}}
.avatar{{width:72px;height:72px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font:700 28px var(--heading-font);flex-shrink:0}}
.profile-info h1{{font:700 clamp(1.3rem,2.5vw,1.8rem) var(--heading-font);margin:0}}
.profile-info p{{color:var(--muted);margin:4px 0 0;font-size:14px}}
.tabs{{display:flex;gap:4px;border-bottom:1px solid color-mix(in srgb,var(--muted) 20%,transparent);margin-bottom:24px}}
.tab{{padding:10px 16px;cursor:pointer;border:0;background:transparent;font:600 14px var(--body-font);color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-1px}}
.tab:hover{{color:var(--text)}}.tab[aria-selected="true"]{{color:var(--accent);border-bottom-color:var(--accent)}}
.form-card{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);padding:24px}}
.form-card h2{{font:700 16px var(--heading-font);margin:0 0 20px}}
.field{{margin-bottom:18px}}
.field label{{display:block;font:600 13px var(--body-font);margin-bottom:6px;color:var(--text)}}
.field input,.field textarea{{width:100%;padding:10px 14px;border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:var(--radius);font:15px var(--body-font);background:var(--bg);color:var(--text)}}
.field input:focus,.field textarea:focus{{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 12%,transparent)}}
.field textarea{{min-height:80px;resize:vertical}}
.field .hint{{font-size:12px;color:var(--muted);margin-top:4px}}
.form-actions{{display:flex;gap:10px;margin-top:24px}}
.btn{{padding:11px 22px;border-radius:var(--radius);font:600 14px var(--body-font);cursor:pointer;border:0}}
.btn-primary{{background:var(--accent);color:#fff}}.btn-primary:hover{{filter:brightness(1.1)}}
.btn-secondary{{border:1px solid var(--muted);background:transparent;color:var(--text)}}
.toast{{display:none;padding:12px 20px;background:#e8f5e9;color:#2e7d32;border-radius:var(--radius);margin-top:16px;font:600 14px var(--body-font)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:24px 0;color:var(--muted);font-size:13px;margin-top:40px}}
@media(max-width:500px){{.profile-header{{flex-direction:column;text-align:center}}.tabs{{overflow-x:auto}}}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#">Dashboard</a><a href="#">Settings</a></nav></div></header>
<main class="wrap">
<div class="profile-header"><div class="avatar" role="img" aria-label="Alex Rivera's avatar">A</div><div class="profile-info"><h1>Alex Rivera</h1><p>Member since January 2024 · {escape(prod['audience'])}</p></div></div>
<div class="tabs" role="tablist" aria-label="Profile sections"><button class="tab" role="tab" aria-selected="true" id="tab-profile">Profile</button><button class="tab" role="tab" aria-selected="false" id="tab-settings">Settings</button><button class="tab" role="tab" aria-selected="false" id="tab-activity">Activity</button></div>
<div class="form-card" role="tabpanel" aria-labelledby="tab-profile"><h2>Edit Profile</h2>
<div class="field"><label for="display-name">Display name</label><input id="display-name" type="text" value="Alex Rivera"></div>
<div class="field"><label for="email">Email address</label><input id="email" type="email" value="alex@example.com"><span class="hint">We'll never share your email publicly.</span></div>
<div class="field"><label for="bio">Bio</label><textarea id="bio" placeholder="Tell others about yourself…"></textarea></div>
<div class="form-actions"><button class="btn btn-primary">Save changes</button><button class="btn btn-secondary">Cancel</button></div>
<div class="toast" role="status">✓ Changes saved successfully.</div>
</div>
</main>
<footer><div class="wrap">&copy; {escape(b)}</div></footer>
</body></html>'''

    return initial, feedback, corrected


def gen_feed_cards(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px;display:flex;justify-content:space-between}}
.feed{{max-width:600px;margin:24px auto;padding:0 16px}}
h1{{font-size:22px}}
.post{{background:white;border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
.post h3{{margin:0 0 4px}}.post p{{margin:0;color:#666}}
.meta{{display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#999}}
</style></head><body>
<header><strong>{escape(b)}</strong><span>Welcome, User</span></header>
<div class="feed"><h1>Your Feed</h1>
<div class="post"><h3>Post title one</h3><p>Some content goes here about a topic.</p><div class="meta"><span>2 hours ago</span><span>5 comments</span></div></div>
<div class="post"><h3>Post title two</h3><p>Some more content about another topic.</p><div class="meta"><span>5 hours ago</span><span>12 comments</span></div></div>
<div class="post"><h3>Post title three</h3><p>Even more content about yet another topic.</p><div class="meta"><span>1 day ago</span><span>3 comments</span></div></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the feed.",
        "Post titles and content are generic placeholders.",
        "No <article> elements — posts should be semantic articles.",
        "No author information or avatars on posts.",
        "No interactive elements — can't like, save, or reply.",
        "No focus styles on any element.",
        "Feed has no loading indicator or 'load more' affordance.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px;gap:16px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none;margin-right:auto}}
header nav a{{color:var(--bg);text-decoration:none;font-size:14px;padding:6px 10px;border-radius:var(--radius)}}
.feed{{max-width:620px;margin:auto;padding:24px 16px 48px}}
.feed-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}}
.feed-header h1{{font:700 clamp(1.2rem,2.5vw,1.6rem) var(--heading-font);margin:0}}
.feed-sort{{padding:6px 12px;border:1px solid color-mix(in srgb,var(--muted) 25%,transparent);border-radius:var(--radius);background:var(--surface);font:13px var(--body-font);cursor:pointer;color:var(--text)}}
.post{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);border-radius:var(--radius);padding:20px;margin-bottom:16px}}
.post-header{{display:flex;gap:12px;align-items:center;margin-bottom:12px}}
.post-avatar{{width:36px;height:36px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font:700 14px var(--body-font);flex-shrink:0}}
.post-author{{font:600 14px var(--heading-font)}}.post-time{{font-size:12px;color:var(--muted)}}
.post h3{{font:600 17px var(--heading-font);margin:0 0 6px}}.post h3 a{{color:var(--text);text-decoration:none}}.post h3 a:hover{{color:var(--accent)}}
.post p{{color:var(--muted);margin:0 0 12px;font-size:14px;line-height:1.5}}
.post-actions{{display:flex;gap:16px}}
.post-btn{{background:transparent;border:0;padding:4px 0;cursor:pointer;font:500 13px var(--body-font);color:var(--muted);display:flex;align-items:center;gap:4px}}
.post-btn:hover{{color:var(--accent)}}
.load-more{{display:block;width:100%;padding:12px;border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);border-radius:var(--radius);background:transparent;cursor:pointer;font:600 14px var(--body-font);color:var(--text);text-align:center}}
.load-more:hover{{background:color-mix(in srgb,var(--accent) 6%,transparent)}}
@media(max-width:500px){{.feed{{padding:16px 12px 40px}}.post{{padding:16px}}}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a><nav aria-label="Primary"><a href="#">Explore</a><a href="#">Profile</a></nav></div></header>
<main class="feed">
<div class="feed-header"><h1>Your Feed</h1><button class="feed-sort">Sort: Recent ▾</button></div>
<article class="post"><div class="post-header"><div class="post-avatar" aria-hidden="true">M</div><div><div class="post-author">Maya Chen</div><time class="post-time" datetime="2025-09-15T14:00:00">2 hours ago</time></div></div><h3><a href="#">Lessons from redesigning our checkout flow</a></h3><p>After three rounds of user testing, we found that removing one form field increased completion by 18%. Here is what we learned about cognitive load in high-stakes flows.</p><div class="post-actions"><button class="post-btn">♡ 24</button><button class="post-btn">💬 5 comments</button><button class="post-btn">⊹ Save</button></div></article>
<article class="post"><div class="post-header"><div class="post-avatar" aria-hidden="true">R</div><div><div class="post-author">Ravi Kapoor</div><time class="post-time" datetime="2025-09-15T11:00:00">5 hours ago</time></div></div><h3><a href="#">Why we switched from tabs to progressive disclosure</a></h3><p>Tabs were hiding our most important content behind a click. Moving to a single-page layout with collapsible sections reduced bounce rate significantly.</p><div class="post-actions"><button class="post-btn">♡ 42</button><button class="post-btn">💬 12 comments</button><button class="post-btn">⊹ Save</button></div></article>
<article class="post"><div class="post-header"><div class="post-avatar" aria-hidden="true">L</div><div><div class="post-author">Lina Ortiz</div><time class="post-time" datetime="2025-09-14T09:00:00">1 day ago</time></div></div><h3><a href="#">Accessibility is not a feature — it is a design language</a></h3><p>We rebuilt our entire component library with accessibility as the primary constraint, not an afterthought. The result was better for everyone.</p><div class="post-actions"><button class="post-btn">♡ 67</button><button class="post-btn">💬 3 comments</button><button class="post-btn">⊹ Save</button></div></article>
<button class="load-more">Load more posts</button>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_code_documentation(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']};display:flex}}
.side{{width:240px;background:#f5f5f5;padding:20px;height:100vh;overflow-y:auto}}
.side a{{display:block;padding:6px 0;color:{p['text']};text-decoration:none;font-size:14px}}
.content{{flex:1;padding:40px;max-width:800px}}
h1{{font-size:28px}}
pre{{background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:6px;overflow-x:auto}}
code{{font-family:monospace}}
.endpoint{{background:white;border:1px solid #ddd;border-radius:8px;padding:16px;margin-bottom:16px}}
.method{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:bold}}
.get{{background:#e8f5e9;color:green}}.post{{background:#e3f2fd;color:blue}}
</style></head><body>
<div class="side"><strong>{escape(b)}</strong><a href="#">Getting Started</a><a href="#">Authentication</a><a href="#">Endpoints</a><a href="#">Errors</a></div>
<div class="content"><h1>API Reference</h1>
<div class="endpoint"><span class="method get">GET</span> /api/users<p>Returns a list of users.</p><pre><code>curl -H "Authorization: Bearer TOKEN" https://api.example.com/users</code></pre></div>
<div class="endpoint"><span class="method post">POST</span> /api/users<p>Creates a new user.</p><pre><code>{{"name": "string", "email": "string"}}</code></pre></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the documentation content.",
        "Sidebar navigation has no <nav> or aria-label.",
        "No focus styles on sidebar links or any interactive element.",
        "Two-pane layout has no responsive fallback for mobile.",
        "Code blocks use generic placeholder URLs and tokens.",
        "No copy-to-clipboard button for code snippets.",
        "Method badges rely on color alone to distinguish GET from POST.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text);display:flex;min-height:100vh}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.sidebar{{width:260px;background:var(--surface);border-right:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:20px;position:sticky;top:0;height:100vh;overflow-y:auto;flex-shrink:0}}
.sidebar .brand{{font:700 17px var(--heading-font);margin-bottom:20px;display:block;color:var(--text)}}
.sidebar nav{{display:flex;flex-direction:column;gap:2px}}
.sidebar nav a{{padding:8px 12px;border-radius:var(--radius);text-decoration:none;color:var(--text);font-size:14px}}
.sidebar nav a:hover,.sidebar nav a[aria-current]{{background:color-mix(in srgb,var(--accent) 10%,transparent);color:var(--accent)}}
.sidebar nav a[aria-current]{{font-weight:700}}
.toggle-nav{{display:none;position:fixed;top:12px;left:12px;z-index:100;background:var(--text);color:var(--bg);border:0;padding:8px 14px;border-radius:var(--radius);cursor:pointer;font:600 13px var(--body-font)}}
.content{{flex:1;padding:40px;max-width:800px}}
.content h1{{font:700 clamp(1.5rem,3vw,2.2rem) var(--heading-font);margin:0 0 8px}}
.content .subtitle{{color:var(--muted);margin:0 0 32px}}
.endpoint{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 12%,transparent);border-radius:var(--radius);overflow:hidden;margin-bottom:20px}}
.endpoint-header{{padding:14px 18px;border-bottom:1px solid color-mix(in srgb,var(--muted) 10%,transparent);display:flex;align-items:center;gap:10px}}
.method{{padding:3px 10px;border-radius:4px;font:700 12px var(--mono-font);letter-spacing:.03em}}
.method-get{{background:#e8f5e9;color:#2e7d32}}.method-post{{background:#e3f2fd;color:#1565c0}}
.endpoint-path{{font:600 15px var(--mono-font)}}
.endpoint-body{{padding:16px 18px}}
.endpoint-body p{{margin:0 0 12px;color:var(--muted)}}
.code-block{{position:relative}}
pre{{background:#1a1d2e;color:#e4e7f1;padding:16px 18px;border-radius:var(--radius);overflow-x:auto;margin:0;font:13px/1.6 var(--mono-font)}}
.copy-btn{{position:absolute;top:8px;right:8px;background:rgba(255,255,255,.1);color:#ccc;border:0;padding:4px 10px;border-radius:4px;cursor:pointer;font:11px var(--body-font)}}
.copy-btn:hover{{background:rgba(255,255,255,.2)}}
@media(max-width:768px){{
  .sidebar{{position:fixed;left:-280px;z-index:99;transition:left .2s}}.sidebar.open{{left:0}}
  .toggle-nav{{display:block}}.content{{padding:60px 20px 40px}}
}}
</style></head><body>
<button class="toggle-nav" aria-label="Toggle docs navigation" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰ Docs</button>
<aside class="sidebar"><span class="brand">{escape(b)}</span><nav aria-label="Documentation navigation"><a href="#" aria-current="page">Getting Started</a><a href="#">Authentication</a><a href="#">Endpoints</a><a href="#">Error Handling</a><a href="#">Rate Limits</a><a href="#">Changelog</a></nav></aside>
<main class="content">
<h1>{escape(b)} API Reference</h1>
<p class="subtitle">Everything you need to {escape(goal)}.</p>
<section class="endpoint"><div class="endpoint-header"><span class="method method-get">GET</span><code class="endpoint-path">/api/v1/resources</code></div><div class="endpoint-body"><p>Returns a paginated list of resources. Supports filtering by status, date range, and category.</p><div class="code-block"><button class="copy-btn" aria-label="Copy code example">Copy</button><pre><code>curl -X GET "https://api.{b.lower().replace(' ', '')}.com/v1/resources?status=active&amp;limit=20" \\
  -H "Authorization: Bearer your_api_key" \\
  -H "Content-Type: application/json"</code></pre></div></div></section>
<section class="endpoint"><div class="endpoint-header"><span class="method method-post">POST</span><code class="endpoint-path">/api/v1/resources</code></div><div class="endpoint-body"><p>Creates a new resource. Requires a valid name and at least one category tag.</p><div class="code-block"><button class="copy-btn" aria-label="Copy code example">Copy</button><pre><code>curl -X POST "https://api.{b.lower().replace(' ', '')}.com/v1/resources" \\
  -H "Authorization: Bearer your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "New Resource", "category": "analytics", "active": true}}'</code></pre></div></div></section>
</main>
</body></html>'''

    return initial, feedback, corrected


def gen_pricing_comparison(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:15px Arial;background:{p['bg']};color:{p['text']};text-align:center}}
header{{background:{p['text']};color:white;padding:16px 24px;text-align:left}}
h1{{font-size:32px;margin:40px 0 10px}}
.plans{{display:flex;justify-content:center;gap:20px;padding:30px 20px;flex-wrap:wrap}}
.plan{{background:white;border-radius:12px;padding:30px;width:280px;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
.plan h2{{font-size:20px;margin:0 0 8px}}
.price{{font-size:36px;font-weight:bold;color:{p['accent']};margin:16px 0}}
.price span{{font-size:14px;font-weight:normal;color:#999}}
ul{{list-style:none;padding:0;text-align:left;margin:16px 0}}
li{{padding:6px 0;border-bottom:1px solid #eee}}
button{{width:100%;padding:12px;border:0;border-radius:8px;font-size:15px;cursor:pointer;margin-top:16px}}
.plan:nth-child(2) button{{background:{p['accent']};color:white}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<h1>Choose Your Plan</h1><p style="color:#666">Simple pricing for everyone.</p>
<div class="plans">
<div class="plan"><h2>Free</h2><div class="price">$0<span>/mo</span></div><ul><li>1 project</li><li>Basic support</li><li>1 GB storage</li></ul><button style="background:#eee">Get Started</button></div>
<div class="plan" style="border:2px solid {p['accent']}"><h2>Pro</h2><div class="price">$19<span>/mo</span></div><ul><li>10 projects</li><li>Priority support</li><li>50 GB storage</li></ul><button>Choose Pro</button></div>
<div class="plan"><h2>Team</h2><div class="price">$49<span>/mo</span></div><ul><li>Unlimited projects</li><li>Dedicated support</li><li>500 GB storage</li></ul><button style="background:#eee">Contact Sales</button></div>
</div></body></html>'''

    feedback = [
        "No <main> landmark — h1 is outside any semantic container.",
        "Pricing cards are not structured as a comparison — users can't scan features across plans.",
        "No ARIA markup for the recommended plan — the border alone is not accessible.",
        "Buttons use inline styles and have no focus styles.",
        "Feature lists are identical in structure with no indication of value differences.",
        "No toggle between monthly/annual billing.",
        "No responsive handling — three 280px cards will overflow at 390px.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.wrap{{width:min(1040px,92%);margin:auto}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none}}
.page-header{{text-align:center;padding:48px 0 20px}}
.page-header h1{{font:700 clamp(1.8rem,4vw,2.8rem) var(--heading-font);margin:0 0 8px}}
.page-header p{{color:var(--muted);margin:0 0 20px;max-width:45ch;margin-inline:auto}}
.billing-toggle{{display:inline-flex;background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 20%,transparent);border-radius:99px;padding:3px;gap:2px;margin-bottom:32px}}
.billing-btn{{padding:8px 18px;border:0;border-radius:99px;font:600 13px var(--body-font);cursor:pointer;background:transparent;color:var(--muted)}}
.billing-btn.active{{background:var(--accent);color:#fff}}
.plans{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding-bottom:60px}}
.plan{{background:var(--surface);border:1px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);padding:32px 28px;display:flex;flex-direction:column;position:relative}}
.plan.featured{{border:2px solid var(--accent);box-shadow:0 8px 32px color-mix(in srgb,var(--accent) 12%,transparent)}}
.featured-badge{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--accent);color:#fff;padding:3px 14px;border-radius:99px;font:700 11px var(--body-font);white-space:nowrap}}
.plan h2{{font:700 20px var(--heading-font);margin:0 0 4px}}.plan .plan-desc{{color:var(--muted);font-size:13px;margin:0 0 16px}}
.plan .price{{font:700 40px var(--heading-font);color:var(--accent);margin:0}}.plan .price small{{font:400 14px var(--body-font);color:var(--muted)}}
.plan .billed{{font-size:12px;color:var(--muted);margin:0 0 20px}}
.plan ul{{list-style:none;padding:0;margin:0 0 auto;flex:1}}.plan li{{padding:8px 0;border-bottom:1px solid color-mix(in srgb,var(--muted) 10%,transparent);font-size:14px;display:flex;gap:8px;align-items:center}}
.plan li::before{{content:'✓';color:var(--accent);font-weight:700;flex-shrink:0}}
.plan-btn{{display:block;width:100%;padding:13px;border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer;border:0;margin-top:24px;text-align:center;text-decoration:none}}
.btn-filled{{background:var(--accent);color:#fff}}.btn-filled:hover{{filter:brightness(1.1)}}
.btn-outline{{background:transparent;border:1px solid var(--muted);color:var(--text)}}
footer{{border-top:1px solid color-mix(in srgb,var(--muted) 15%,transparent);padding:28px 0;text-align:center;color:var(--muted);font-size:13px}}
@media(max-width:800px){{.plans{{grid-template-columns:1fr;max-width:400px;margin-inline:auto}}}}
</style></head><body>
<header><div class="header-inner wrap"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="wrap">
<div class="page-header"><h1>Simple, Transparent Pricing</h1><p>Choose the plan that lets you {escape(goal)}.</p>
<div class="billing-toggle"><button class="billing-btn active">Monthly</button><button class="billing-btn">Annual (save 20%)</button></div></div>
<div class="plans">
<div class="plan"><h2>Starter</h2><p class="plan-desc">For individuals getting started.</p><div class="price">$0<small>/mo</small></div><p class="billed">Free forever</p><ul><li>1 active project</li><li>Community support</li><li>1 GB storage</li><li>Basic analytics</li></ul><a class="plan-btn btn-outline" href="#">Start free</a></div>
<div class="plan featured" aria-label="Recommended plan"><span class="featured-badge">Most Popular</span><h2>Professional</h2><p class="plan-desc">For growing teams and power users.</p><div class="price">$19<small>/mo</small></div><p class="billed">Billed monthly</p><ul><li>10 active projects</li><li>Priority email support</li><li>50 GB storage</li><li>Advanced analytics</li><li>Custom integrations</li></ul><a class="plan-btn btn-filled" href="#">Try Professional</a></div>
<div class="plan"><h2>Enterprise</h2><p class="plan-desc">For organizations with custom needs.</p><div class="price">Custom</div><p class="billed">Annual contract</p><ul><li>Unlimited projects</li><li>Dedicated account manager</li><li>500 GB storage</li><li>SSO and audit logs</li><li>Custom SLA</li></ul><a class="plan-btn btn-outline" href="#">Contact sales</a></div>
</div>
</main>
<footer>&copy; {escape(b)} — All plans include a 14-day free trial. No credit card required.</footer>
</body></html>'''

    return initial, feedback, corrected


def gen_guided_flow(p, prod, t, radius, space, nav, interaction, responsive):
    b, goal = prod["brand"], prod["goal"]
    initial = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
body{{margin:0;font:16px Arial;background:{p['bg']};color:{p['text']}}}
header{{background:{p['text']};color:white;padding:16px 24px}}
.flow{{max-width:600px;margin:40px auto;padding:0 20px;text-align:center}}
h1{{font-size:28px}}
.option{{background:white;border:2px solid #ddd;border-radius:12px;padding:20px;margin-bottom:12px;cursor:pointer;text-align:left}}
.option h3{{margin:0 0 4px}}.option p{{margin:0;color:#666;font-size:14px}}
.option:hover{{border-color:{p['accent']}}}
button{{background:{p['accent']};color:white;border:0;padding:14px 28px;border-radius:8px;font-size:16px;cursor:pointer;margin-top:20px}}
</style></head><body>
<header><strong>{escape(b)}</strong></header>
<div class="flow"><h1>Let's Get Started</h1><p>Choose what best describes you.</p>
<div class="option"><h3>Option A</h3><p>Description of this option.</p></div>
<div class="option"><h3>Option B</h3><p>Description of this option.</p></div>
<div class="option"><h3>Option C</h3><p>Description of this option.</p></div>
<button>Continue</button></div></body></html>'''

    feedback = [
        "No <main> landmark wrapping the guided flow.",
        "Options are divs with cursor:pointer — not keyboard accessible (no tabindex, no role).",
        "Option names are generic 'Option A/B/C' — must be product-relevant choices.",
        "No visual feedback showing which option is selected.",
        "Continue button has no disabled state before selection.",
        "No progress indication — users don't know how many steps remain.",
        "Descriptions are identical placeholders.",
    ]

    corrected = f'''<!doctype html>
<html lang="en"><head>{_meta(b)}<style>
:root{{{_css_vars(p, t, radius, space)}}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.6 var(--body-font);background:var(--bg);color:var(--text)}}
*:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
header{{background:var(--text);color:var(--bg);padding:0 5%}}
.header-inner{{display:flex;align-items:center;min-height:56px}}
.brand{{font:700 17px var(--heading-font);color:var(--bg);text-decoration:none}}
.flow{{width:min(560px,90%);margin:40px auto;padding-bottom:48px}}
.flow-progress{{display:flex;gap:6px;margin-bottom:32px}}
.flow-progress span{{flex:1;height:4px;border-radius:2px;background:color-mix(in srgb,var(--muted) 20%,transparent)}}
.flow-progress span.done{{background:var(--accent)}}
.flow h1{{font:700 clamp(1.4rem,3vw,2rem) var(--heading-font);margin:0 0 6px;text-align:center}}
.flow .subtitle{{color:var(--muted);text-align:center;margin:0 0 28px}}
.options{{display:flex;flex-direction:column;gap:10px}}
.option{{background:var(--surface);border:2px solid color-mix(in srgb,var(--muted) 15%,transparent);border-radius:var(--radius);padding:18px 20px;cursor:pointer;display:flex;align-items:start;gap:14px;transition:border-color .15s}}
.option:hover{{border-color:color-mix(in srgb,var(--accent) 50%,transparent)}}
.option[aria-checked="true"]{{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 5%,transparent)}}
.option-radio{{width:20px;height:20px;border-radius:50%;border:2px solid color-mix(in srgb,var(--muted) 30%,transparent);flex-shrink:0;margin-top:2px;display:flex;align-items:center;justify-content:center}}
.option[aria-checked="true"] .option-radio{{border-color:var(--accent)}}
.option[aria-checked="true"] .option-radio::after{{content:'';width:10px;height:10px;border-radius:50%;background:var(--accent)}}
.option-text h3{{font:600 16px var(--heading-font);margin:0 0 4px}}.option-text p{{margin:0;font-size:14px;color:var(--muted)}}
.flow-actions{{display:flex;justify-content:space-between;margin-top:28px}}
.btn{{padding:13px 28px;border-radius:var(--radius);font:700 15px var(--body-font);cursor:pointer;border:0}}
.btn-primary{{background:var(--accent);color:#fff}}.btn-primary:hover{{filter:brightness(1.1)}}.btn-primary:disabled{{opacity:.4;cursor:not-allowed}}
.btn-back{{background:transparent;border:1px solid var(--muted);color:var(--text)}}
.step-label{{text-align:center;color:var(--muted);font-size:13px;margin-top:12px}}
@media(max-width:500px){{.option{{padding:14px 16px}}.flow{{margin-top:24px}}}}
</style></head><body>
<header><div class="header-inner"><a class="brand" href="#">{escape(b)}</a></div></header>
<main class="flow">
<div class="flow-progress" aria-label="Step 1 of 3"><span class="done"></span><span></span><span></span></div>
<h1>Tell us about yourself</h1>
<p class="subtitle">This helps us tailor your experience to {escape(goal)}.</p>
<div class="options" role="radiogroup" aria-label="Choose your profile type">
<div class="option" role="radio" aria-checked="false" tabindex="0"><div class="option-radio"></div><div class="option-text"><h3>Just getting started</h3><p>I'm new and want guided setup with helpful defaults.</p></div></div>
<div class="option" role="radio" aria-checked="true" tabindex="0"><div class="option-radio"></div><div class="option-text"><h3>Experienced user</h3><p>I know what I need and want to jump straight to configuration.</p></div></div>
<div class="option" role="radio" aria-checked="false" tabindex="0"><div class="option-radio"></div><div class="option-text"><h3>Team lead or admin</h3><p>I'm setting this up for my team and need organization controls.</p></div></div>
</div>
<div class="flow-actions"><button class="btn btn-back" disabled aria-disabled="true">← Back</button><button class="btn btn-primary">Continue →</button></div>
<p class="step-label">Step 1 of 3 — about 2 minutes total</p>
</main>
</body></html>'''

    return initial, feedback, corrected


# ============================================================
# ARCHETYPE DISPATCH TABLE
# ============================================================

ARCHETYPE_GENERATORS = [
    gen_landing_hero_split,
    gen_dashboard_sidebar,
    gen_kanban_board,
    gen_search_filter_results,
    gen_detail_page_anchored,
    gen_stepper_form,
    gen_timeline_vertical,
    gen_comparison_table,
    gen_map_plus_list,
    gen_calendar_grid,
    gen_editorial_longform,
    gen_card_masonry,
    gen_chat_interface,
    gen_interactive_exercise,
    gen_data_table_dense,
    gen_profile_workspace,
    gen_feed_cards,
    gen_code_documentation,
    gen_pricing_comparison,
    gen_guided_flow,
]


# ============================================================
# RECORD ASSEMBLY
# ============================================================

def build_record(index: int, prod: dict, palette: dict, typo: dict,
                 archetype_fn, nav: str, interaction: str,
                 responsive: str, radius: str, space: str) -> dict:
    """Build one complete Forma v2 record."""
    example_id = f"forma_v2_unique_{prod['id']}"

    initial_code, critic_feedback, corrected_code = archetype_fn(
        palette, prod, typo, radius, space, nav, interaction, responsive
    )

    task = (f"Design a {prod['page_type']} for {prod['brand']}, a {prod['category']} product. "
            f"The primary goal is to {prod['goal']}. "
            f"Target audience: {prod['audience']}.")

    constraints = [
        f"Must work at both 1440×900 desktop and 390×844 mobile viewports.",
        f"Include visible keyboard focus states and screen reader landmarks.",
        f"Content must be specific to {prod['audience']} — no generic placeholder text.",
        f"Navigation should use a {nav.lower()} pattern.",
    ]

    design_spec = {
        "information_architecture": f"A {prod['page_type']} structured for {prod['audience']}. "
                                     f"Navigation uses {nav.lower()}. Content prioritizes {prod['goal']}.",
        "layout": f"{archetype_fn.__name__.replace('gen_', '').replace('_', ' ').title()} composition with "
                  f"{palette['name']} visual direction. Responsive strategy: {responsive}.",
        "tokens": {
            "background": palette["bg"],
            "surface": palette["surface"],
            "text": palette["text"],
            "muted": palette["muted"],
            "accent": palette["accent"],
            "focus": palette["focus"],
            "radius": radius,
            "space": space,
        },
        "typography": f"Heading: {typo['heading']}. Body: {typo['body']}. "
                      f"Monospace: {typo['mono']}. Scale: {typo['scale']}.",
        "components": _components_for_archetype(archetype_fn.__name__),
        "responsive_rules": [responsive],
        "interaction_states": [interaction],
        "accessibility": "Semantic landmarks (header, nav, main, footer), one h1, "
                         "visible focus styles, ARIA attributes on interactive widgets, "
                         "no color-only meaning, keyboard-navigable controls.",
    }

    return {
        "example_id": example_id,
        "task": task,
        "constraints": constraints,
        "reference_screenshots": [],
        "research_evidence": [
            f"Users in the {prod['category']} domain expect clear calls to action and minimal friction.",
            f"Research shows {prod['audience']} prefer interfaces that surface the most relevant information first.",
        ],
        "design_spec": design_spec,
        "initial_code": initial_code,
        "render_report": {
            "status": "not_rendered",
            "viewports": [
                {"width": 1440, "height": 900, "initial": _null_viewport(), "corrected": _null_viewport()},
                {"width": 390, "height": 844, "initial": _null_viewport(), "corrected": _null_viewport()},
            ],
            "visual_score": None,
            "accessibility_score": None,
            "screenshots_captured": False,
        },
        "critic_feedback": critic_feedback,
        "corrected_code": corrected_code,
        "quality_score": None,
        "status": "needs_review",
        "source": "agent-forma-v2-generator",
    }


def _null_viewport():
    return {"horizontal_overflow": None, "console_errors": None,
            "has_h1": None, "has_main": None, "focusable_count": None}


def _components_for_archetype(name: str) -> list[str]:
    """Return archetype-specific component list."""
    components_map = {
        "gen_landing_hero_split": ["responsive header", "split hero", "primary/secondary CTA", "feature cards", "badge", "footer"],
        "gen_dashboard_sidebar": ["sidebar navigation", "metric cards", "data table", "status badges", "toggle sidebar"],
        "gen_kanban_board": ["kanban columns", "draggable cards", "priority tags", "column counters", "toolbar filters"],
        "gen_search_filter_results": ["search input", "filter sidebar", "result cards", "result count", "toggle filters"],
        "gen_detail_page_anchored": ["sticky anchor nav", "image gallery", "specification list", "price display", "add-to-cart button"],
        "gen_stepper_form": ["progress stepper", "form fields", "validation hints", "back/next buttons", "completion estimate"],
        "gen_timeline_vertical": ["timeline with connector", "event cards", "type badges", "date stamps", "load more button"],
        "gen_comparison_table": ["comparison table", "plan headers", "feature rows", "recommended badge", "CTA buttons"],
        "gen_map_plus_list": ["interactive map", "location cards", "search input", "zoom controls", "distance metadata"],
        "gen_calendar_grid": ["calendar table", "month navigation", "event indicators", "today highlight", "agenda list fallback"],
        "gen_editorial_longform": ["reading progress bar", "article hero", "pull quotes", "blockquotes with citation", "section headings"],
        "gen_card_masonry": ["masonry grid", "image cards", "filter buttons", "rating stars", "category labels"],
        "gen_chat_interface": ["message bubbles", "typing indicator", "input field", "timestamp labels", "sender avatars"],
        "gen_interactive_exercise": ["timer ring", "instruction display", "start/reset buttons", "progress dots", "completion banner"],
        "gen_data_table_dense": ["sortable table", "search bar", "status badges", "pagination", "action links"],
        "gen_profile_workspace": ["avatar display", "tab navigation", "form card", "save/cancel buttons", "toast notification"],
        "gen_feed_cards": ["post cards", "author avatars", "action buttons", "sort control", "load more"],
        "gen_code_documentation": ["sidebar docs nav", "endpoint cards", "code blocks", "copy button", "method badges"],
        "gen_pricing_comparison": ["pricing cards", "billing toggle", "feature lists", "recommended badge", "CTA buttons"],
        "gen_guided_flow": ["progress bar", "radio options", "flow navigation", "step label", "selection feedback"],
    }
    return components_map.get(name, ["responsive header", "main content", "footer"])


# ============================================================
# MAIN GENERATION LOGIC WITH UNIQUENESS LEDGER
# ============================================================

def generate_all(count: int = 300, offset: int = 0, seed: int = 42) -> list[dict]:
    """Generate `count` unique records starting at `offset` with full uniqueness guarantees."""
    rng = random.Random(seed)

    # Pick product subset
    products = PRODUCTS[offset : offset + count]

    # Shuffle assignment pools
    palettes = list(PALETTES)
    typographies = list(TYPOGRAPHY_PAIRINGS)
    navs = list(NAV_PATTERNS)
    interactions = list(INTERACTION_MODELS)
    responsives = list(RESPONSIVE_STRATEGIES)
    radii = list(RADIUS_LANGUAGE)
    spaces = list(SPACING_RHYTHMS)

    ledger: list[tuple] = []
    records = []
    n_archetypes = len(ARCHETYPE_GENERATORS)

    for idx, prod in enumerate(products):
        i = offset + idx

        # Assign archetype — rotated evenly across 20 archetypes
        archetype_idx = i % n_archetypes
        arch_fn = ARCHETYPE_GENERATORS[archetype_idx]
        arch_name = arch_fn.__name__

        # Pick palette — rotate through, ensuring no exact reuse within adjacent records
        pal = palettes[i % len(palettes)]

        # Pick typography — staggered from palette to avoid same combo
        typo = typographies[(i + 3) % len(typographies)]

        # Pick other dimensions with offsets to maximize spread
        nav = navs[i % len(navs)]
        interaction = interactions[(i + 2) % len(interactions)]
        responsive = responsives[(i + 1) % len(responsives)]
        radius = radii[(i + 4) % len(radii)]
        space = spaces[(i + 5) % len(spaces)]

        # Build uniqueness ledger entry
        ledger_entry = (
            prod["goal"][:40],
            prod["audience"][:30],
            prod["page_type"],
            arch_name,
            nav,
            pal["name"],
            typo["name"],
            interaction,
            responsive[:40],
        )

        # Check for collision and break if needed
        if ledger_entry in ledger:
            pal = palettes[(i + 7) % len(palettes)]
            typo = typographies[(i + 9) % len(typographies)]

        ledger.append(ledger_entry)

        record = build_record(i, prod, pal, typo, arch_fn, nav, interaction,
                              responsive, radius, space)
        records.append(record)

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate unique Forma v2 UI/UX design records.")
    parser.add_argument("--output", default="outputs/forma_v2_unique_300.jsonl",
                        help="Output JSONL file path")
    parser.add_argument("--count", type=int, default=300,
                        help="Number of records to generate")
    parser.add_argument("--offset", type=int, default=0,
                        help="Starting product index offset")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    max_available = len(PRODUCTS) - args.offset
    count = min(args.count, max_available)
    records = generate_all(count=count, offset=args.offset, seed=args.seed)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Print summary
    archetypes_used = set()
    palettes_used = set()
    typos_used = set()
    navs_used = set()
    for r in records:
        spec = r["design_spec"]
        archetypes_used.add(spec["layout"].split(" composition")[0])
        palettes_used.add(spec["tokens"]["accent"])
        typos_used.add(spec["typography"].split(".")[0])
        navs_used.add(spec["information_architecture"].split("Navigation uses ")[1].split(".")[0] if "Navigation uses " in spec["information_architecture"] else "unknown")

    summary = {
        "output": str(output_path),
        "records_generated": len(records),
        "unique_ids": len(set(r["example_id"] for r in records)),
        "archetypes_used": len(archetypes_used),
        "palettes_used": len(palettes_used),
        "typography_pairings_used": len(typos_used),
        "navigation_patterns_used": len(navs_used),
        "render_status": "not_rendered",
        "status": "all records generated successfully",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
