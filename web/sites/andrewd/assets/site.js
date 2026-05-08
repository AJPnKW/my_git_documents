const storageKey = "andrewdSupportRoadmapDynamicV5";

function byId(id){ return document.getElementById(id); }
function selected(id){ const el = byId(id); return el ? el.value : ""; }
function checkedValues(name){ return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value); }
function setText(selector, text){ const el = document.querySelector(selector); if(el) el.textContent = text; }

function labelFor(value, fallback = "Not answered"){
  const labels = {
    on_odsp:"On ODSP", thinks_on_odsp:"May be on ODSP", not_on_odsp:"Not on ODSP", unknown:"I do not know",
    yes:"Yes", no:"No",
    eligible_connected:"Eligible / connected", application_started:"Application started", not_started:"Not started", not_sure:"I do not know / I have not been told", not_eligible:"Told not eligible",
    has_passport:"Have Passport funding", pending:"May be pending / waiting", none:"No / not connected",
    terminated_quickly:"Jobs often end shortly after starting", struggles_keep_job:"Can get work but struggle to keep it", not_working:"Not currently working", looking:"Looking for work",
    left_college:"Left or had to stop college/training", wants_return:"Want to return", currently_student:"Currently a student", not_current_goal:"Not a current goal"
  };
  return labels[value] || fallback;
}

function goTab(tab){
  document.querySelectorAll(".tab-panel").forEach(panel => panel.classList.remove("active"));
  document.querySelectorAll(".nav-tab").forEach(button => button.classList.remove("active"));
  const panel = byId(tab);
  const button = document.querySelector(`.nav-tab[data-tab="${tab}"]`);
  if(panel) panel.classList.add("active");
  if(button) button.classList.add("active");
  document.body.dataset.activeTab = tab;
  const hero = document.querySelector(".hero");
  if(hero) hero.hidden = tab !== "dashboard";
  history.replaceState(null, "", "#" + tab);
  window.scrollTo({top:0, behavior:"smooth"});
}

document.addEventListener("click", event => {
  const tabButton = event.target.closest("[data-tab]");
  if(tabButton) goTab(tabButton.dataset.tab);
  const goButton = event.target.closest("[data-go]");
  if(goButton) goTab(goButton.dataset.go);
});

window.addEventListener("load", () => {
  enhancePageForAccessibility();
  const startTab = location.hash ? location.hash.replace("#","") : "dashboard";
  goTab(byId(startTab) ? startTab : "dashboard");
  loadAnswers(false);
});

function collectAnswers(){
  return {
    odspStatus:selected("odspStatus"), odspWorker:selected("odspWorker"), odspSupports:checkedValues("odspSupports"),
    dsoStatus:selected("dsoStatus"), passportStatus:selected("passportStatus"), supportNeeds:checkedValues("supportNeeds"),
    jobPattern:selected("jobPattern"), employmentSupports:checkedValues("employmentSupports"), workBarriers:checkedValues("workBarriers"),
    educationStatus:selected("educationStatus"), documents:checkedValues("documents"),
    mainGoal:byId("mainGoal")?.value.trim() || "", contextNotes:byId("contextNotes")?.value.trim() || ""
  };
}

function restoreAnswers(data){
  Object.entries(data).forEach(([key,value]) => { const field = byId(key); if(field && typeof value === "string") field.value = value; });
  ["odspSupports","supportNeeds","employmentSupports","workBarriers","documents"].forEach(name => {
    document.querySelectorAll(`input[name="${name}"]`).forEach(el => { el.checked = Array.isArray(data[name]) && data[name].includes(el.value); });
  });
}

function saveAnswers(){ localStorage.setItem(storageKey, JSON.stringify(collectAnswers())); updateDashboard(); generateRoadmap(false); }
function loadAnswers(showMessage = true){
  const raw = localStorage.getItem(storageKey);
  if(!raw){ updateDashboard(); if(showMessage && byId("roadmapSummary")) byId("roadmapSummary").innerHTML = "No saved answers found on this browser."; return; }
  restoreAnswers(JSON.parse(raw)); updateDashboard(); generateRoadmap(false);
}
function clearAnswers(){
  localStorage.removeItem(storageKey);
  document.querySelectorAll("select, textarea").forEach(el => el.value = "");
  document.querySelectorAll("input[type='checkbox']").forEach(el => el.checked = false);
  updateDashboard(); resetTables(); if(byId("roadmapSummary")) byId("roadmapSummary").innerHTML = "Answers cleared. Complete the Inquiry again.";
}

function row(cells){
  const labels = ["Order","Step","Why","Ask / Action","Contact"];
  return "<tr>" + cells.map((cell, index) => `<td data-label="${labels[index] || "Item"}">${cell}</td>`).join("") + "</tr>";
}
function gapRow(area,status,gap,action){ return `<tr><td data-label="Area">${area}</td><td data-label="Current status">${status}</td><td data-label="Gap">${gap}</td><td data-label="Next action">${action}</td></tr>`; }
function chip(text,type){ return `<span class="status-chip ${type || ""}">${text}</span>`; }

function updateDashboard(){
  const a = collectAnswers();
  const chips = [];
  if(a.odspStatus) chips.push(chip("ODSP: " + labelFor(a.odspStatus), a.odspStatus === "on_odsp" ? "good" : "warn"));
  if(a.odspWorker) chips.push(chip("ODSP worker: " + labelFor(a.odspWorker), a.odspWorker === "yes" ? "good" : "warn"));
  if(a.dsoStatus) chips.push(chip("DSO: " + labelFor(a.dsoStatus), a.dsoStatus === "eligible_connected" ? "good" : "warn"));
  if(a.passportStatus) chips.push(chip("Passport: " + labelFor(a.passportStatus), a.passportStatus === "has_passport" ? "good" : "warn"));
  if(a.jobPattern) chips.push(chip("Work: " + labelFor(a.jobPattern), ["terminated_quickly","struggles_keep_job"].includes(a.jobPattern) ? "warn" : "good"));
  if(a.educationStatus) chips.push(chip("Education: " + labelFor(a.educationStatus), a.educationStatus === "not_current_goal" ? "good" : "warn"));
  const snapshot = byId("dashboardSnapshot");
  if(snapshot) snapshot.innerHTML = chips.length ? chips.join("") : "<p>No inquiry answers saved yet.</p>";
  const readiness = byId("readinessText");
  if(readiness) readiness.textContent = chips.length >= 4 ? "Your roadmap is ready to review. You can still improve it by answering more questions." : "Answer what you know first. The roadmap still works with uncertain answers.";
}

function resetTables(){
  const pathway = byId("pathwayTable"); const gap = byId("gapTable");
  if(pathway) pathway.querySelector("tbody").innerHTML = row(["—","No roadmap yet","Complete inquiry first.","Use the Inquiry tab.","—"]);
  if(gap) gap.querySelector("tbody").innerHTML = gapRow("—","No answers yet","—","Complete inquiry.");
  if(byId("generatedScript")) byId("generatedScript").textContent = "Complete the inquiry first.";
  if(byId("plainTextPlan")) byId("plainTextPlan").textContent = "Complete the inquiry first.";
}

function generateRoadmap(switchTab = true){
  const a = collectAnswers(); const steps = []; const gaps = []; const plain = [];
  const odspKnown = a.odspStatus === "on_odsp" || a.odspStatus === "thinks_on_odsp";
  const odspSupportMissing = a.odspSupports.includes("income_only") || a.odspSupports.includes("unknown") || !a.odspSupports.includes("employment_supports") || !a.odspSupports.includes("job_retention");
  const dsoMissing = ["not_started","not_sure",""] .includes(a.dsoStatus);
  const passportMissing = ["none","unknown",""] .includes(a.passportStatus);
  const jobRetentionNeed = ["terminated_quickly","struggles_keep_job"].includes(a.jobPattern);
  const educationNeed = ["left_college","wants_return"].includes(a.educationStatus);
  const docsWeak = a.documents.includes("none") || a.documents.includes("not_gathered") || a.documents.includes("doc_unknown") || a.documents.length < 2;
  plain.push("YOUR SUPPORT ROADMAP", "====================", "");
  if(odspKnown){
    steps.push(["1","ODSP caseworker check","You may already have a formal support path through ODSP.","Ask for ODSP Employment Supports, job-retention support, provider referral, and written next steps.","ODSP Kitchener: 519-886-4700"]);
    gaps.push(["ODSP","Connected or likely connected", odspSupportMissing ? "Employment/retention support is unclear or not yet documented." : "Some employment support appears to exist.", "Confirm worker, employment supports, retention plan, and written next steps."]);
  } else {
    steps.push(["1","Confirm ODSP status","ODSP status is missing or unclear.","Call 211 or ODSP Kitchener to confirm status and the correct contact path.","211 or ODSP Kitchener"]);
    gaps.push(["ODSP","Not confirmed","ODSP status and worker path unclear.","Confirm whether ODSP applies and who owns the file."]);
  }
  if(dsoMissing){
    steps.push(["2","Start or confirm DSO intake","DSO may be the doorway to longer-term developmental-service supports.","Call DSO Central West and ask whether eligibility/application should be started or updated.","DSO Central West: 1-888-941-1121"]);
    gaps.push(["DSO","Not started / unclear","Developmental-service pathway may be missing.","Call DSO and ask what documentation is required."]);
  } else {
    steps.push(["2","Update DSO support profile","If DSO is already active, the support needs may need updating.","Ask DSO to capture employment, daily living, forms/calls, planning, education, and community support needs.","DSO Central West"]);
    gaps.push(["DSO",labelFor(a.dsoStatus),"Support profile may not reflect current needs.","Ask for review/update."]);
  }
  if(passportMissing){
    steps.push(["3","Check Passport funding","Passport may fund supports that short-term programs do not cover.","Ask DSO whether Passport is available, pending, or needs follow-up.","DSO Central West"]);
    gaps.push(["Passport",labelFor(a.passportStatus),"Funding status unclear or unavailable.","Ask DSO and KW Habilitation about Passport/fee-for-service paths."]);
  } else {
    steps.push(["3","Use Passport strategically","Passport may help pay for agency support or person-directed planning.","Ask KW Habilitation whether Passport can be used for KW Career Compass or planning supports.","KW Habilitation: 519-744-6307"]);
    gaps.push(["Passport",labelFor(a.passportStatus),"Need to map funding to actual services.","Ask for eligible service options."]);
  }
  if(jobRetentionNeed){
    steps.push(["4","Employment retention support","Repeated early job loss points to support after hiring, not only job search.","Ask for job coaching, work-fit assessment, on-the-job training, employer support, and follow-up after hire.","KW Career Compass + Starling"]);
    gaps.push(["Employment",labelFor(a.jobPattern),"Job retention support is likely the central gap.","Use KW Career Compass and Starling; do not stop at resume/interview help."]);
  } else {
    steps.push(["4","Employment planning","Work status still needs structured support.","Ask for skills assessment, job matching, and realistic work environment planning.","Starling / Employment Ontario"]);
    gaps.push(["Employment",labelFor(a.jobPattern),"Need to confirm fit and support level.","Book an employment advisor appointment."]);
  }
  if(educationNeed){
    steps.push(["5","Conestoga support path","Training or college should not restart without support planning.","Contact Accessible Learning before re-enrolment and ask for documentation review, accommodation planning, and whether Academic Guidance should be involved.","Conestoga Accessible Learning"]);
    gaps.push(["Education",labelFor(a.educationStatus),"Return path may fail again without accommodations.","Accessible Learning first; Academic Guidance and Health & Wellness if needed."]);
  } else {
    gaps.push(["Education",labelFor(a.educationStatus),"Not the immediate pathway unless you choose it.","Keep as later goal."]);
  }
  if(docsWeak){
    steps.push(["6","Build a document folder","Applications and accommodations can stall when documents are hard to find.","Gather what you can: ODSP letters, assessments, school records, college records, resume, and job history. Ask for help finding missing documents.","Personal prep step"]);
    gaps.push(["Documents","Not yet gathered / unclear","Records may exist but are not organized yet.","Create one folder and one job/school timeline."]);
  } else {
    gaps.push(["Documents","Some records identified","Documents still need to be organized.","Create one folder and bring copies to calls."]);
  }
  steps.push(["7","Self-advocacy script","Support works better when needs are clear and next steps are written down.","Ask: What program is this? What can you help with? What happens next? Can you send that in writing?","Use the Advocate tab"]);
  if(byId("pathwayTable")) byId("pathwayTable").querySelector("tbody").innerHTML = steps.map(s => row(s)).join("");
  if(byId("gapTable")) byId("gapTable").querySelector("tbody").innerHTML = gaps.map(g => gapRow(g[0],g[1],g[2],g[3])).join("");
  const supportNeedText = a.supportNeeds.length ? a.supportNeeds.join(", ").replaceAll("_"," ") : "employment, job retention, forms, planning, and follow-through";
  if(byId("generatedScript")) byId("generatedScript").textContent = ["Call script:","","I am trying to connect with the right supports. I need help understanding what applies to me and what to do next.", odspKnown ? "I am on or may be on ODSP, and I need to confirm what my ODSP worker can do for employment supports and job retention." : "My ODSP status or worker information is unclear and needs to be confirmed.", dsoMissing ? "My DSO status is not clear, so I need to know whether an application should be started." : "DSO may already be active, but my support profile may need to be updated.", passportMissing ? "Passport funding is not confirmed, so I need to ask whether it is available, pending, or possible." : "Passport funding may exist, so I need to know what employment or planning supports it can pay for.", "The support areas to capture are: " + supportNeedText + ".", "Please send the next steps in writing."].join("\n");
  plain.push("Current snapshot", "- ODSP: " + labelFor(a.odspStatus), "- ODSP worker known: " + labelFor(a.odspWorker), "- DSO: " + labelFor(a.dsoStatus), "- Passport: " + labelFor(a.passportStatus), "- Work pattern: " + labelFor(a.jobPattern), "- Education: " + labelFor(a.educationStatus), "", "First actions");
  steps.forEach(s => plain.push(`${s[0]}. ${s[1]} — ${s[3]} Contact: ${s[4]}.`));
  if(a.mainGoal){ plain.push("", "Main goal: " + a.mainGoal); }
  if(a.contextNotes){ plain.push("", "Context notes: " + a.contextNotes); }
  if(byId("plainTextPlan")) byId("plainTextPlan").textContent = plain.join("\n");
  if(byId("roadmapSummary")) byId("roadmapSummary").innerHTML = `<strong>Roadmap generated.</strong> First focus: ${jobRetentionNeed ? "job-retention support plus ODSP/DSO/Passport coordination." : "confirm existing supports and build a structured employment/education plan."}`;
  updateDashboard(); localStorage.setItem(storageKey, JSON.stringify(a)); if(switchTab) goTab("roadmap");
}

function enhancePageForAccessibility(){
  refineHero(); updateNavigation(); simplifyDashboardIntro(); layoutDashboard(); layoutRoadmap(); addAdvocateTab(); addConestogaDepth(); addCommunityTips(); addResourceBlocks(); addContactsTools(); addAiNotice(); addTodoLink();
}

function refineHero(){
  const hero = document.querySelector(".hero"); if(!hero) return;
  setText(".hero .eyebrow", "Waterloo Region / KW support workflow");
  setText(".hero h2", "This tool gives you a step-by-step path for ODSP, DSO, Passport, employment supports, education supports, documents, and accommodation rights.");
  setText(".hero p:not(.eyebrow)", "Answer the inquiry. Generate your roadmap. Use the contact plan.");
  hero.classList.add("dashboard-hero");
}

function updateNavigation(){
  const nav = document.querySelector(".side-nav"); if(!nav) return;
  if(!nav.querySelector('[data-tab="advocate"]')){
    const education = nav.querySelector('[data-tab="education"]');
    if(education){ const advocate = document.createElement("button"); advocate.className = "nav-tab"; advocate.dataset.tab = "advocate"; advocate.innerHTML = '<span class="nav-icon">📣</span><span class="nav-text">9 Advocate</span>'; education.insertAdjacentElement("afterend", advocate); }
  }
  const rights = nav.querySelector('[data-tab="rights"] .nav-text'); const contacts = nav.querySelector('[data-tab="contacts"] .nav-text');
  if(rights) rights.textContent = "10 Rights"; if(contacts) contacts.textContent = "11 Contacts";
}

function addTodoLink(){
  const nav = document.querySelector(".side-nav");
  if(nav && !nav.querySelector('a[href="project_todo.html"]')) nav.insertAdjacentHTML("beforeend", '<a class="nav-link" href="project_todo.html"><span class="nav-icon">📋</span><span class="nav-text">TODO</span></a>');
}

function simplifyDashboardIntro(){
  const intro = document.querySelector("#dashboard .workflow-intro"); if(!intro) return;
  intro.innerHTML = `<article class="start-card"><span>1</span><h3>Start with what you know</h3><p>Use <strong>“I do not know”</strong> when something is unclear. That answer is useful because it shows where support is missing.</p></article><article class="start-card"><span>2</span><h3>Find the support gap</h3><p>The tool checks ODSP, DSO, Passport, employment, education, documents, and accommodation support.</p></article><article class="start-card"><span>3</span><h3>Ask for written next steps</h3><p>Every call should end with who to contact next, what documents are needed, and when to follow up.</p></article>`;
  const head = document.querySelector("#dashboard .section-head p"); if(head) head.textContent = "Start here. Answer what you can, then use the roadmap to decide who to contact first.";
}

function layoutDashboard(){
  const dashboard = byId("dashboard"); if(!dashboard || dashboard.querySelector(".dashboard-two-column")) return;
  const intro = dashboard.querySelector(".workflow-intro"); const grid = dashboard.querySelector(".dashboard-grid");
  const firstHeading = Array.from(dashboard.querySelectorAll("h3")).find(h => h.textContent.trim() === "What to look at first"); const firstTable = firstHeading ? firstHeading.nextElementSibling : null;
  if(!intro || !grid || !firstHeading || !firstTable) return;
  const wrap = document.createElement("div"); wrap.className = "dashboard-two-column"; const left = document.createElement("div"); left.className = "dashboard-left"; const right = document.createElement("div"); right.className = "dashboard-right";
  intro.parentNode.insertBefore(wrap, intro); left.appendChild(intro); left.appendChild(grid); right.appendChild(firstHeading); right.appendChild(firstTable); wrap.appendChild(left); wrap.appendChild(right);
}

function layoutRoadmap(){
  const roadmap = byId("roadmap"); if(!roadmap || roadmap.querySelector(".roadmap-three-column")) return;
  const summary = byId("roadmapSummary");
  const headings = Array.from(roadmap.querySelectorAll("h3"));
  const pathwayHeading = headings.find(h => h.textContent.includes("Suggested Pathway")); const gapHeading = headings.find(h => h.textContent.includes("Support Gap")); const scriptHeading = headings.find(h => h.textContent.includes("Call Script"));
  if(!summary || !pathwayHeading || !gapHeading || !scriptHeading) return;
  const wrap = document.createElement("div"); wrap.className = "roadmap-three-column";
  const makeCol = (heading) => { const col = document.createElement("article"); col.className = "roadmap-card"; const next = heading.nextElementSibling; col.appendChild(heading); if(next) col.appendChild(next); return col; };
  summary.insertAdjacentElement("afterend", wrap); wrap.appendChild(makeCol(pathwayHeading)); wrap.appendChild(makeCol(gapHeading)); wrap.appendChild(makeCol(scriptHeading));
}

function addAdvocateTab(){
  if(byId("advocate")) return; const rights = byId("rights"); if(!rights) return;
  const section = document.createElement("section"); section.id = "advocate"; section.className = "tab-panel";
  section.innerHTML = `<div class="section-head"><h2>📣 Being Your Own Advocate</h2><p>Advocacy means asking clear questions, writing down answers, and making sure next steps are not left vague.</p></div><div class="callout"><strong>Plain meaning:</strong> You do not need to know the system. You can ask the worker or organization to explain the system and write down what happens next.</div><table><thead><tr><th>Situation</th><th>What to say</th><th>Why it helps</th></tr></thead><tbody><tr><td data-label="Situation">I do not understand the program</td><td data-label="What to say">“Can you explain what this program does in plain language?”</td><td data-label="Why">You should not have to guess what a service does.</td></tr><tr><td data-label="Situation">I am unsure what happens next</td><td data-label="What to say">“Can you send me the next steps in writing?”</td><td data-label="Why">Written steps reduce memory pressure and confusion.</td></tr><tr><td data-label="Situation">I may miss details</td><td data-label="What to say">“Can I bring a support person or take notes?”</td><td data-label="Why">A second person can help track instructions and deadlines.</td></tr><tr><td data-label="Situation">The support may be short-term</td><td data-label="What to say">“How long does this support last, and what happens when it ends?”</td><td data-label="Why">Short-term programs can leave gaps if there is no follow-up plan.</td></tr><tr><td data-label="Situation">I need job support</td><td data-label="What to say">“Do you help after I start the job, or only before I get hired?”</td><td data-label="Why">Job-retention support is different from job-search support.</td></tr></tbody></table><h3>Communication checklist</h3><table><thead><tr><th>Write down</th><th>Example</th></tr></thead><tbody><tr><td data-label="Write down">Date and time</td><td data-label="Example">April 29, 2:00 PM</td></tr><tr><td data-label="Write down">Organization and person</td><td data-label="Example">ODSP Kitchener — worker name or main office</td></tr><tr><td data-label="Write down">What you asked</td><td data-label="Example">Employment supports, DSO, Passport, job retention, documents</td></tr><tr><td data-label="Write down">What they said</td><td data-label="Example">Referral needed / intake form / waitlist / next appointment</td></tr><tr><td data-label="Write down">Next step and deadline</td><td data-label="Example">Call back by Friday if no response</td></tr></tbody></table><h3>Make sure the organization answers these</h3><ul class="plain-list"><li>What program am I talking to?</li><li>Am I eligible or do I need an intake first?</li><li>Is this short-term, long-term, or waitlisted?</li><li>Who is my contact person or team?</li><li>What documents do I need?</li><li>What happens after the first appointment?</li><li>Can you send the next steps in writing?</li></ul>`;
  rights.parentNode.insertBefore(section, rights);
}

function addConestogaDepth(){
  const education = byId("education"); if(!education || education.querySelector(".conestoga-depth")) return;
  education.insertAdjacentHTML("beforeend", `<div class="conestoga-depth"><h3>🎓 Conestoga return-to-school checklist</h3><table><thead><tr><th>Need</th><th>Ask this</th><th>Why</th></tr></thead><tbody><tr><td data-label="Need">Before applying or restarting</td><td data-label="Ask this">“Can I speak with Accessible Learning before I restart?”</td><td data-label="Why">Conestoga lists pre-admission appointments for prospective students considering applying.</td></tr><tr><td data-label="Need">Documentation unclear</td><td data-label="Ask this">“I do not know what documents I have. Can you tell me what is enough and what is missing?”</td><td data-label="Why">Conestoga says to indicate if you have no documentation or are unsure; support and suggestions may still be provided.</td></tr><tr><td data-label="Need">Prior school difficulty</td><td data-label="Ask this">“Can we review what went wrong before and build a re-entry plan?”</td><td data-label="Why">The goal is to plan accommodations and supports before classes restart.</td></tr><tr><td data-label="Need">Course load or pace</td><td data-label="Ask this">“Can I discuss reduced course load, program fit, or academic guidance?”</td><td data-label="Why">Academic Guidance can help with decisions, goals, and referrals to supports.</td></tr><tr><td data-label="Need">Stress or wellness support</td><td data-label="Ask this">“What counselling, wellness, or peer supports are available if I am enrolled?”</td><td data-label="Why">Conestoga lists counselling, peer wellness, and health promotion supports for students.</td></tr></tbody></table><div class="callout"><strong>Safe wording:</strong> Do not ask for records to be changed without knowing the rules. Ask whether a note, appeal, academic standing review, accommodation review, or re-entry plan is available.</div></div>`);
}

function addCommunityTips(){
  const advocate = byId("advocate"); if(!advocate || advocate.querySelector(".community-tips")) return;
  advocate.insertAdjacentHTML("beforeend", `<div class="community-tips"><h3>💬 Community tips to consider</h3><p class="small">These are practical lived-experience themes. They are not official policy. Confirm rules with the organization.</p><table><thead><tr><th>Theme</th><th>Practical use</th></tr></thead><tbody><tr><td data-label="Theme">Ask for things in writing</td><td data-label="Practical use">After every call, ask for the next step, documents needed, and follow-up date in writing.</td></tr><tr><td data-label="Theme">Do not understate needs</td><td data-label="Practical use">For DSO or support intake, mention every genuine barrier that affects work, school, forms, calls, appointments, transportation, or follow-through.</td></tr><tr><td data-label="Theme">Track names and dates</td><td data-label="Practical use">Write down who you spoke with, what they said, and when to follow up.</td></tr><tr><td data-label="Theme">Ask if support is short-term or ongoing</td><td data-label="Practical use">A course or resume program may end quickly. Ask what happens after the program or after you start work.</td></tr></tbody></table></div>`);
}

function addResourceBlocks(){
  addResourceBlock("odsp", "💼 ODSP resources", [["ODSP overview","https://www.ontario.ca/page/ontario-disability-support-program"],["ODSP Employment Supports","https://www.ontario.ca/document/ontario-disability-support-program-policy-directives-employment-supports/11-introduction"],["ODSP Job retention","https://www.ontario.ca/document/ontario-disability-support-program-policy-directives-employment-supports/42-job-retention"],["ODSP Kitchener contact","https://211ontario.ca/service/73444788/ontario-ministry-of-community-and-social-services-ontario-disability-support-program/"]]);
  addResourceBlock("dso", "🤝 DSO + Passport resources", [["DSO Central West","https://www.dsocwr.ca/"],["How to access DSO services","https://www.dsontario.ca/how-to-access-services"],["Passport guidelines","https://www.ontario.ca/page/passport-program-guidelines"]]);
  addResourceBlock("employment", "🛠️ Employment resources", [["KW Career Compass","https://kwhab.ca/services/employment/"],["Starling Employment Services","https://www.ontario.ca/locations/employment-training/92922495-kitchener-165-king-st-e"],["ODSP job retention policy","https://www.ontario.ca/document/ontario-disability-support-program-policy-directives-employment-supports/42-job-retention"]]);
  addResourceBlock("education", "🎓 Conestoga resources", [["Accessible Learning","https://studentsuccess.conestogac.on.ca/accessible-learning"],["Accessible Learning intake form","https://conestogac-accommodate.symplicity.com/public_accommodation/"],["Academic Guidance","https://studentsuccess.conestogac.on.ca/academic-guidance"],["Health and Wellness","https://studentsuccess.conestogac.on.ca/health-and-wellness"]]);
}
function addResourceBlock(sectionId, title, links){
  const section = byId(sectionId); if(!section || section.querySelector(".resource-links")) return;
  const block = document.createElement("div"); block.className = "resource-links"; block.innerHTML = `<h3>${title}</h3><p>Use these links to check phone numbers, intake steps, eligibility rules, and program details.</p><div>${links.map(([text,url]) => `<a href="${url}" target="_blank" rel="noopener">${text}</a>`).join("")}</div>`; section.appendChild(block);
}
function addContactsTools(){
  const contacts = byId("contacts"); if(!contacts || contacts.querySelector(".contact-tools")) return;
  contacts.insertAdjacentHTML("afterbegin", `<div class="contact-tools"><h3>📇 Add organization contacts</h3><p>Download a contact file for ODSP, DSO, employment, Conestoga, and other support organizations.</p><a class="primary" href="assets/andrewd_support_contacts.vcf" download>Add organization contacts</a></div>`);
}
function addAiNotice(){
  const main = byId("main"); if(!main || byId("aiNotice")) return;
  const note = document.createElement("details"); note.id = "aiNotice"; note.className = "ai-notice"; note.innerHTML = `<summary>Review note</summary><p>This guide was drafted with help from ChatGPT. Details may be incomplete or incorrect. Confirm program rules, eligibility, forms, contact details, and deadlines directly with each organization.</p>`; main.appendChild(note);
}

function addAndrewContactLink(){
  const nav = document.querySelector(".side-nav");
  if(nav && !nav.querySelector('a[href="contact_andrew.html"]')){
    nav.insertAdjacentHTML("beforeend", '<a class="nav-link" href="contact_andrew.html"><span class="nav-icon">🙋</span><span class="nav-text">Contact Andrew P</span></a>');
  }
}


