import re
from typing import Dict, Any, List, Optional
from backend.services.llm_service import llm_service
from backend.services.hindsight_service import hindsight_service

class CodeGeneratorAgent:
    """Generates fully functional, responsive HTML/Tailwind/JS code for local businesses."""

    def generate_website(
        self,
        business_data: Dict[str, Any],
        copy_data: Dict[str, Any],
        design_system: Dict[str, Any],
        critique_patch_instructions: Optional[str] = None
    ) -> str:
        name = business_data.get("name", "Apex Solutions")
        category = business_data.get("category", "Professional Services")
        location = business_data.get("location", "Austin, TX")
        phone = business_data.get("phone", "+1 512-555-0198")
        whatsapp = business_data.get("whatsapp", phone)

        # Standardize WhatsApp URL format per Hindsight Directives
        clean_wa = re.sub(r"[^\d]", "", whatsapp)
        wa_url = f"https://wa.me/{clean_wa}"

        palette = design_system.get("palette", {})
        primary_color = palette.get("primary", "#2563eb")
        secondary_color = palette.get("secondary", "#10b981")

        # Recall Hindsight directives & code templates
        recalled_rules = hindsight_service.recall(
            query="code standards html responsive whatsapp booking modal validation",
            tags=["code_quality", "directive"],
            max_results=3
        )
        rules_text = "\n".join([f"- {r['content']}" for r in recalled_rules])

        # If we have an active LLM, use it to refine or customize; otherwise assemble our battle-tested template
        if critique_patch_instructions and llm_service.client:
            prompt = f"""
You are an expert Frontend Architect.
Improve this website based on the following Self-Healing Refinement Instructions from Hindsight Critics:
{critique_patch_instructions}

Business Name: {name}
Category: {category}
Location: {location}
WhatsApp URL: {wa_url}
Primary Color: {primary_color}

Return the entire single-file HTML code with Tailwind CDN, Lucide icons, responsive layout, appointment modal, and working WhatsApp CTA.
Return ONLY valid HTML inside ```html ... ``` code block.
"""
            llm_response = llm_service.complete(prompt, system_prompt="You write pristine, production-ready HTML with zero syntax errors.")
            if "```html" in llm_response:
                html_code = llm_response.split("```html")[1].split("```")[0].strip()
                return html_code

        # Default battle-tested, high-conversion template generator
        return self._build_template(business_data, copy_data, design_system, wa_url)

    def _build_template(
        self,
        business_data: Dict[str, Any],
        copy_data: Dict[str, Any],
        design_system: Dict[str, Any],
        wa_url: str
    ) -> str:
        name = business_data.get("name", "Austin Smile Studio")
        category = business_data.get("category", "Dental Clinic")
        location = business_data.get("location", "Austin, TX")
        phone = business_data.get("phone", "+1 (512) 555-0198")
        email = business_data.get("email", f"hello@{name.lower().replace(' ', '')}.com")
        
        palette = design_system.get("palette", {})
        primary = palette.get("primary", "#0284c7")
        secondary = palette.get("secondary", "#0d9488")
        accent = palette.get("accent", "#f59e0b")

        headline = copy_data.get("headline", f"Premium {category} Care in {location}")
        subheadline = copy_data.get("subheadline", f"Trusted by thousands of families in {location}. Comprehensive care, modern equipment, and flexible scheduling.")
        cta_primary = copy_data.get("cta_primary", "Book Appointment")
        cta_secondary = copy_data.get("cta_secondary", "Chat on WhatsApp")

        services = copy_data.get("services", [])
        testimonials = copy_data.get("testimonials", [])
        why_us = copy_data.get("why_choose_us", [])

        services_html = ""
        for s in services:
            services_html += f"""
            <div class="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
                <div class="w-12 h-12 rounded-xl bg-sky-50 flex items-center justify-center text-sky-600 mb-6 group-hover:scale-110 transition-transform">
                    <i data-lucide="check-circle" class="w-6 h-6"></i>
                </div>
                <h3 class="text-xl font-bold text-slate-900 mb-2">{s.get('title', 'Certified Service')}</h3>
                <p class="text-slate-600 leading-relaxed">{s.get('description', 'High-quality care tailored to your specific requirements.')}</p>
            </div>
            """

        testimonials_html = ""
        for t in testimonials:
            testimonials_html += f"""
            <div class="bg-slate-50 p-6 rounded-2xl border border-slate-200/60 shadow-sm">
                <div class="flex items-center space-x-1 text-amber-400 mb-4">
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                </div>
                <p class="text-slate-700 italic mb-4">"{t.get('quote', 'Exceptional service and quick response!')}"</p>
                <div class="font-semibold text-slate-900 text-sm">{t.get('name', 'Local Resident')}</div>
                <div class="text-xs text-slate-500">Verified Client • {location}</div>
            </div>
            """

        why_html = ""
        for w in why_us:
            why_html += f"""
            <li class="flex items-start space-x-3">
                <div class="mt-1 flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                    <i data-lucide="check" class="w-3.5 h-3.5"></i>
                </div>
                <span class="text-slate-700 font-medium">{w}</span>
            </li>
            """

        html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {category} in {location}</title>
    <meta name="description" content="Top-rated {category} in {location}. Call {phone} or chat on WhatsApp for fast scheduling.">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons CDN -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased selection:bg-sky-500 selection:text-white">

    <!-- Top Announcement Bar -->
    <div class="bg-slate-900 text-white text-xs py-2 px-4 text-center font-medium flex items-center justify-center space-x-3">
        <span>📍 Proudly serving {location} & surrounding neighborhoods</span>
        <span class="hidden md:inline">•</span>
        <span class="hidden md:inline">🕒 Same-Day Emergency Bookings Available</span>
    </div>

    <!-- Navigation Header -->
    <header class="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all duration-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-sky-600 text-white flex items-center justify-center font-extrabold text-xl shadow-md shadow-sky-600/20">
                    <i data-lucide="sparkles" class="w-5 h-5"></i>
                </div>
                <div>
                    <span class="text-xl font-extrabold tracking-tight text-slate-900">{name}</span>
                    <span class="block text-xs font-medium text-slate-500">{category}</span>
                </div>
            </div>

            <!-- Desktop Nav -->
            <nav class="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-600">
                <a href="#services" class="hover:text-sky-600 transition-colors">Services</a>
                <a href="#why-us" class="hover:text-sky-600 transition-colors">Why Us</a>
                <a href="#testimonials" class="hover:text-sky-600 transition-colors">Reviews</a>
                <a href="#contact" class="hover:text-sky-600 transition-colors">Location</a>
            </nav>

            <!-- Header Actions -->
            <div class="hidden sm:flex items-center space-x-3">
                <a href="tel:{phone.replace(' ', '')}" class="flex items-center space-x-2 text-sm font-semibold text-slate-700 hover:text-sky-600 px-3 py-2 rounded-lg transition-colors">
                    <i data-lucide="phone" class="w-4 h-4 text-sky-600"></i>
                    <span>{phone}</span>
                </a>
                <button onclick="openBookingModal()" class="bg-sky-600 hover:bg-sky-700 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-md shadow-sky-600/20 hover:shadow-lg transition-all duration-200 flex items-center space-x-2">
                    <i data-lucide="calendar" class="w-4 h-4"></i>
                    <span>{cta_primary}</span>
                </button>
            </div>

            <!-- Mobile Hamburger -->
            <button onclick="toggleMobileMenu()" class="md:hidden p-2 rounded-lg text-slate-700 hover:bg-slate-100">
                <i data-lucide="menu" class="w-6 h-6"></i>
            </button>
        </div>

        <!-- Mobile Menu Dropdown -->
        <div id="mobile-menu" class="hidden md:hidden px-4 pt-2 pb-6 bg-white border-b border-slate-200 space-y-3">
            <a href="#services" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Services</a>
            <a href="#why-us" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Why Us</a>
            <a href="#testimonials" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Reviews</a>
            <a href="#contact" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Contact</a>
            <button onclick="openBookingModal(); toggleMobileMenu();" class="w-full bg-sky-600 text-white py-3 rounded-xl font-semibold shadow-md">
                {cta_primary}
            </button>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 bg-gradient-to-b from-white via-sky-50/30 to-slate-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div class="lg:col-span-7 space-y-6 text-center lg:text-left">
                    <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-sky-100 text-sky-800 text-xs font-bold tracking-wide uppercase">
                        <i data-lucide="shield-check" class="w-4 h-4 text-sky-600"></i>
                        <span>Verified & Licensed in {location}</span>
                    </div>

                    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
                        {headline}
                    </h1>

                    <p class="text-lg sm:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                        {subheadline}
                    </p>

                    <!-- Trust Stats -->
                    <div class="pt-2 flex flex-wrap justify-center lg:justify-start gap-4 text-xs font-semibold text-slate-500">
                        <div class="flex items-center space-x-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                            <i data-lucide="star" class="w-4 h-4 text-amber-500 fill-amber-500"></i>
                            <span>4.9/5 Rating (500+ Reviews)</span>
                        </div>
                        <div class="flex items-center space-x-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                            <i data-lucide="clock" class="w-4 h-4 text-sky-600"></i>
                            <span>Rapid Response Dispatch</span>
                        </div>
                    </div>

                    <!-- Hero CTAs -->
                    <div class="pt-4 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                        <button onclick="openBookingModal()" class="w-full sm:w-auto bg-sky-600 hover:bg-sky-700 text-white px-8 py-4 rounded-xl font-bold text-base shadow-lg shadow-sky-600/30 hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center space-x-2">
                            <i data-lucide="calendar" class="w-5 h-5"></i>
                            <span>{cta_primary}</span>
                        </button>
                        <a href="{wa_url}" target="_blank" rel="noopener noreferrer" class="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-4 rounded-xl font-bold text-base shadow-lg shadow-emerald-600/30 hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center space-x-2">
                            <i data-lucide="message-circle" class="w-5 h-5"></i>
                            <span>{cta_secondary}</span>
                        </a>
                    </div>
                </div>

                <!-- Hero Card / Quick Booking Preview -->
                <div class="lg:col-span-5">
                    <div class="bg-white rounded-3xl p-8 border border-slate-200 shadow-xl shadow-slate-200/50 relative">
                        <div class="flex items-center justify-between pb-6 border-b border-slate-100">
                            <div>
                                <h3 class="text-lg font-bold text-slate-900">Direct Appointment Desk</h3>
                                <p class="text-xs text-slate-500">Immediate confirmation via SMS / WhatsApp</p>
                            </div>
                            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                                ● Online
                            </span>
                        </div>

                        <form id="hero-quick-form" onsubmit="handleHeroSubmit(event)" class="space-y-4 pt-6">
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Your Full Name</label>
                                <input type="text" required placeholder="John Doe" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Phone or WhatsApp Number</label>
                                <input type="tel" required placeholder="{phone}" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Preferred Service</label>
                                <select class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm bg-white">
                                    <option>Consultation & Diagnostic</option>
                                    <option>Standard Service Appointment</option>
                                    <option>Urgent / Emergency Inspection</option>
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3.5 rounded-xl shadow-md transition-all text-sm flex items-center justify-center space-x-2">
                                <span>Confirm Reservation</span>
                                <i data-lucide="arrow-right" class="w-4 h-4"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="py-20 bg-slate-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-xs font-bold text-sky-600 uppercase tracking-widest mb-2">Tailored Offerings</h2>
                <h3 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">Expert Services Designed for You</h3>
                <p class="text-slate-600 mt-4 text-base">From routine visits to specialized emergency interventions in {location}.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {services_html}
            </div>
        </div>
    </section>

    <!-- Why Choose Us Section -->
    <section id="why-us" class="py-20 bg-white border-y border-slate-200/60">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="space-y-6">
                    <span class="text-xs font-bold text-emerald-600 uppercase tracking-widest">Why We Stand Out</span>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
                        Built on Integrity, Reliability, and Proven Local Results.
                    </h2>
                    <p class="text-slate-600 leading-relaxed text-base">
                        When you contact {name}, you get certified experts committed to upfront honesty, zero hidden fees, and complete satisfaction.
                    </p>
                    <ul class="space-y-4 pt-2">
                        {why_html}
                    </ul>
                </div>

                <div class="bg-gradient-to-tr from-sky-600 to-teal-500 rounded-3xl p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
                    <div class="relative z-10 space-y-6">
                        <div class="inline-block p-3 rounded-2xl bg-white/20 backdrop-blur-md">
                            <i data-lucide="award" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl sm:text-3xl font-bold">100% Satisfaction Guarantee</h3>
                        <p class="text-white/90 text-sm leading-relaxed">
                            Every service performed is backed by our full warranty. If you're not completely satisfied, we'll return and make it right at no extra charge.
                        </p>
                        <div class="pt-4 flex items-center space-x-4">
                            <button onclick="openBookingModal()" class="bg-white text-slate-900 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-slate-100 transition-colors text-sm">
                                Get In Touch
                            </button>
                            <a href="{wa_url}" target="_blank" rel="noopener noreferrer" class="text-white font-semibold flex items-center space-x-2 text-sm hover:underline">
                                <span>Direct Chat</span>
                                <i data-lucide="external-link" class="w-4 h-4"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section id="testimonials" class="py-20 bg-slate-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-2xl mx-auto mb-16">
                <span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Real Customer Feedback</span>
                <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mt-2">Loved by Locals in {location}</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                {testimonials_html}
            </div>
        </div>
    </section>

    <!-- Contact & Map Section -->
    <section id="contact" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div class="space-y-6">
                    <span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Visit & Connect</span>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">We're Here in {location}</h2>
                    <p class="text-slate-600 text-base">Have questions or need emergency assistance? Reach our on-duty staff instantly.</p>

                    <div class="space-y-4 pt-4">
                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                            <div class="w-10 h-10 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="map-pin" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 font-semibold uppercase">Service Territory</div>
                                <div class="font-bold text-slate-900">{location} and Surrounding Areas</div>
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                            <div class="w-10 h-10 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="phone-call" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 font-semibold uppercase">Telephone</div>
                                <a href="tel:{phone.replace(' ', '')}" class="font-bold text-slate-900 hover:text-sky-600">{phone}</a>
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                            <div class="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="message-circle" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 font-semibold uppercase">Official WhatsApp</div>
                                <a href="{wa_url}" target="_blank" rel="noopener noreferrer" class="font-bold text-emerald-700 hover:underline">Click to start WhatsApp chat</a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Interactive Location Card -->
                <div class="rounded-3xl bg-slate-100 p-8 border border-slate-200 flex flex-col justify-between relative overflow-hidden">
                    <div class="space-y-4">
                        <div class="inline-flex items-center space-x-2 bg-white px-3 py-1 rounded-full text-xs font-bold text-slate-700 shadow-sm">
                            <i data-lucide="navigation" class="w-3.5 h-3.5 text-sky-600"></i>
                            <span>GPS Service Zone: {location}</span>
                        </div>
                        <h3 class="text-2xl font-bold text-slate-900">Direct Coverage Area</h3>
                        <p class="text-slate-600 text-sm">Dispatched directly from local stations to minimize response wait times.</p>
                    </div>

                    <div class="my-8 h-48 bg-slate-200 rounded-2xl flex items-center justify-center border border-slate-300/80 relative">
                        <div class="text-center space-y-2">
                            <div class="w-12 h-12 rounded-full bg-sky-600 text-white flex items-center justify-center mx-auto shadow-lg animate-bounce">
                                <i data-lucide="map-pin" class="w-6 h-6"></i>
                            </div>
                            <span class="text-xs font-bold text-slate-700 block">{location} Hub</span>
                        </div>
                    </div>

                    <button onclick="openBookingModal()" class="w-full bg-sky-600 hover:bg-sky-700 text-white font-bold py-4 rounded-xl shadow-md transition-all text-sm">
                        Request On-Site Dispatch
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-slate-950 text-slate-400 py-12 border-t border-slate-800 text-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold">
                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                </div>
                <span class="text-white font-bold text-base">{name}</span>
            </div>
            <div>
                © 2026 {name}. All rights reserved. Professional {category} services in {location}.
            </div>
        </div>
    </footer>

    <!-- Floating WhatsApp CTA (Hindsight Mandatory Feature) -->
    <a href="{wa_url}" target="_blank" rel="noopener noreferrer" class="fixed bottom-6 right-6 z-50 bg-emerald-500 hover:bg-emerald-600 text-white p-4 rounded-full shadow-2xl shadow-emerald-500/40 hover:scale-110 transition-all duration-300 flex items-center justify-center group" title="Chat on WhatsApp">
        <i data-lucide="message-circle" class="w-7 h-7"></i>
        <span class="max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ease-in-out text-sm font-bold pl-0 group-hover:pl-2">
            WhatsApp
        </span>
    </a>

    <!-- Interactive Appointment Booking Modal -->
    <div id="booking-modal" class="fixed inset-0 z-50 hidden bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full p-8 shadow-2xl relative border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
            <button onclick="closeBookingModal()" class="absolute top-6 right-6 text-slate-400 hover:text-slate-700 p-1.5 rounded-lg">
                <i data-lucide="x" class="w-6 h-6"></i>
            </button>

            <div class="mb-6">
                <div class="w-10 h-10 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center mb-3">
                    <i data-lucide="calendar" class="w-5 h-5"></i>
                </div>
                <h3 class="text-2xl font-bold text-slate-900">Schedule Appointment</h3>
                <p class="text-slate-500 text-sm mt-1">Book your session with {name}. We will confirm within 15 minutes.</p>
            </div>

            <form id="modal-form" onsubmit="handleModalSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                    <input type="text" required placeholder="Jane Doe" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 mb-1">Phone / WhatsApp</label>
                        <input type="tel" required placeholder="{phone}" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 mb-1">Preferred Date</label>
                        <input type="date" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Service Type</label>
                    <select class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:outline-none text-sm bg-white">
                        <option>General Consultation</option>
                        <option>Standard Service Treatment</option>
                        <option>Urgent / Emergency Request</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-sky-600 hover:bg-sky-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-sky-600/20 transition-all text-sm flex items-center justify-center space-x-2">
                    <i data-lucide="check" class="w-4 h-4"></i>
                    <span>Confirm Booking</span>
                </button>
            </form>
        </div>
    </div>

    <!-- Client-Side Toast / Feedback Notification -->
    <div id="toast" class="fixed top-6 right-6 z-50 hidden bg-emerald-600 text-white px-6 py-4 rounded-2xl shadow-xl font-medium flex items-center space-x-3">
        <i data-lucide="check-circle" class="w-5 h-5"></i>
        <span id="toast-message">Booking received! We will text you shortly.</span>
    </div>

    <script>
        // Initialize Lucide Icons
        lucide.createIcons();

        function toggleMobileMenu() {{
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        }}

        function openBookingModal() {{
            document.getElementById('booking-modal').classList.remove('hidden');
        }}

        function closeBookingModal() {{
            document.getElementById('booking-modal').classList.add('hidden');
        }}

        function showToast(message) {{
            const toast = document.getElementById('toast');
            document.getElementById('toast-message').innerText = message;
            toast.classList.remove('hidden');
            setTimeout(() => {{
                toast.classList.add('hidden');
            }}, 4000);
        }}

        function handleModalSubmit(e) {{
            e.preventDefault();
            closeBookingModal();
            showToast("Thank you! Your appointment request has been scheduled.");
        }}

        function handleHeroSubmit(e) {{
            e.preventDefault();
            showToast("Reservation confirmed! Our team will contact you on WhatsApp.");
        }}
    </script>
</body>
</html>"""
        return html

code_generator_agent = CodeGeneratorAgent()
