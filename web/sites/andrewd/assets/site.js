const storageKey = "andrewdSupportRoadmapDynamicV1";

function byId(id){ return document.getElementById(id); }

function selected(id){
  const el = byId(id);
  return el ? el.value : "";
}

function checkedValues(name){
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
}

function labelFor(value, fallback = "Not answered"){
  const labels = {
    on_odsp:"On ODSP", thinks_on_odsp:"Thinks he is on ODSP", not_on_odsp:"Not on ODSP", unknown:"Not sure",
    yes:"Yes", no:"No",
    eligible_connected:"Eligible / connected", application_started:"Application started", not_started:"Not started", not_sure:"Not sure", not_eligible:"Known not eligible",
    has_passport:"Has Passport funding", pending:"Pending / waiting", none:"None", 
    terminated_quickly:"Often terminated shortly after starting", struggles_keep_job:"Can get work but struggles to keep it", not_working:"Not currently working", looking:"Looking for work",
    left_college:"Left or had to stop college/training", wants_return:"Wants to return", currently_student:"Currently a student", not_current_goal:"Not a current goal"
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
  history.replaceState(null, "", "#" + tab);
  window.scrollTo({top:0, behavior:"smooth"});
}

document.addEventListener("click", event => {
  const tabButton = event.target.closest("[data-tab]");
  if(tabButton){ goTab(tabButton.dataset.tab); }
  const goButton = event.target.closest("[data-go]");
  if(goButton){ goTab(goButton.dataset.go); }
});

window.addEventListener("load", () => {
  const startTab = location.hash ? location.hash.replace("#","") : "dashboard";
  if(byId(startTab)) goTab(startTab);
  loadAnswers(false);
});

function collectAnswers(){
  return {
    odspStatus:selected("odspStatus"),
    odspWorker:selected("odspWorker"),
    odspSupports:checkedValues("odspSupports"),
    dsoStatus:selected("dsoStatus"),
    passportStatus:selected("passportStatus"),
    supportNeeds:checkedValues("supportNeeds"),
    jobPattern:selected("jobPattern"),
    employmentSupports:checkedValues("employmentSupports"),
    workBarriers:checkedValues("workBarriers"),
    educationStatus:selected("educationStatus"),
    documents:checkedValues("documents"),
    mainGoal:byId("mainGoal")?.value.trim() || "",
    contextNotes:byId("contextNotes")?.value.trim() || ""
  };
}

function restoreAnswers(data){
  Object.entries(data).forEach(([key,value]) => {
    const field = byId(key);
    if(field && typeof value === "string") field.value = value;
  });
  ["odspSupports","supportNeeds","employmentSupports","workBarriers","documents"].forEach(name => {
    document.querySelectorAll(`input[name="${name}"]`).forEach(el => {
      el.checked = Array.isArray(data[name]) && data[name].includes(el.value);
    });
  });
}

function saveAnswers(){
  localStorage.setItem(storageKey, JSON.stringify(collectAnswers()));
  updateDashboard();
  generateRoadmap(false);
}

function loadAnswers(showMessage = true){
  const raw = localStorage.getItem(storageKey);
  if(!raw){
    updateDashboard();
    if(showMessage) byId("roadmapSummary").innerHTML = "No saved answers found on this browser.";
    return;
  }
  restoreAnswers(JSON.parse(raw));
  updateDashboard();
  generateRoadmap(false);
}

function clearAnswers(){
  localStorage.removeItem(storageKey);
  document.querySelectorAll("select, textarea").forEach(el => el.value = "");
  document.querySelectorAll("input[type='checkbox']").forEach(el => el.checked = false);
  updateDashboard();
  byId("roadmapSummary").innerHTML = "Answers cleared. Complete the Workflow Inquiry again.";
  resetTables();
}

function row(cells){
  return "<tr>" + cells.map((cell, index) => {
    const labels = ["Order","Step","Why","Ask / Action","Contact"];
    return `<td data-label="${labels[index] || "Item"}">${cell}</td>`;
  }).join("") + "</tr>";
}

function gapRow(area,status,gap,action){
  return `<tr><td data-label="Area">${area}</td><td data-label="Current status">${status}</td><td data-label="Gap">${gap}</td><td data-label="Next action">${action}</td></tr>`;
}

function updateDashboard(){
  const a = collectAnswers();
  const chips = [];
  if(a.odspStatus) chips.push(chip("ODSP: " + labelFor(a.odspStatus), a.odspStatus === "on_odsp" ? "good" : "warn"));
  if(a.odspWorker) chips.push(chip("ODSP worker: " + labelFor(a.odspWorker), a.odspWorker === "yes" ? "good" : "warn"));
  if(a.dsoStatus) chips.push(chip("DSO: " + labelFor(a.dsoStatus), a.dsoStatus === "eligible_connected" ? "good" : "warn"));
  if(a.passportStatus) chips.push(chip("Passport: " + labelFor(a.passportStatus), a.passportStatus === "has_passport" ? "good" : "warn"));
  if(a.jobPattern) chips.push(chip("Work: " + labelFor(a.jobPattern), a.jobPattern === "terminated_quickly" || a.jobPattern === "struggles_keep_job" ? "warn" : "good"));
  if(a.educationStatus) chips.push(chip("Education: " + labelFor(a.educationStatus), a.educationStatus === "not_current_goal" ? "good" : "warn"));

  byId("dashboardSnapshot").innerHTML = chips.length ? chips.join("") : "<p>No inquiry answers saved yet.</p>";
  const readiness = chips.length >= 4 ? "Roadmap can be generated from the saved inquiry answers." : "Complete more inquiry fields to improve the roadmap.";
  byId("readinessText").textContent = readiness;
}

function chip(text,type){ return `<span class="status-chip ${type || ""}">${text}</span>`; }

function resetTables(){
  byId("pathwayTable").querySelector("tbody").innerHTML = row(["—","No roadmap yet","Complete inquiry first.","Use the Workflow Inquiry tab.","—"]);
  byId("gapTable").querySelector("tbody").innerHTML = gapRow("—","No answers yet","—","Complete inquiry.");
  byId("generatedScript").textContent = "Complete the inquiry first.";
  byId("plainTextPlan").textContent = "Complete the inquiry first.";
}

function generateRoadmap(switchTab = true){
  const a = collectAnswers();
  const steps = [];
  const gaps = [];
  const plain = [];

  const odspKnown = a.odspStatus === "on_odsp" || a.odspStatus === "thinks_on_odsp";
  const odspSupportMissing = a.odspSupports.includes("income_only") || a.odspSupports.includes("unknown") || !a.odspSupports.includes("employment_supports") || !a.odspSupports.includes("job_retention");
  const dsoMissing = ["not_started","not_sure",""].includes(a.dsoStatus);
  const passportMissing = ["none","unknown",""].includes(a.passportStatus);
  const jobRetentionNeed = ["terminated_quickly","struggles_keep_job"].includes(a.jobPattern);
  const educationNeed = ["left_college","wants_return"].includes(a.educationStatus);
  const docsWeak = a.documents.includes("none") || a.documents.length < 2;

  plain.push("ANDREW D SUPPORT ROADMAP");
  plain.push("========================");
  plain.push("");

  if(odspKnown){
    steps.push(["1","ODSP caseworker check","He is already connected to ODSP, so this is the fastest formal support path.","Ask for ODSP Employment Supports, job-retention support, provider referral, and written next steps.","ODSP Kitchener: 519-886-4700"]);
    gaps.push(["ODSP","Connected or likely connected", odspSupportMissing ? "Employment/retention support is unclear or missing." : "Some employment support appears to exist.", "Confirm worker, employment supports, retention plan, and written next steps."]);
  } else {
    steps.push(["1","Confirm ODSP status","ODSP status is missing or unclear.","Call 211 or ODSP Kitchener to confirm status and the correct contact path.","211 or ODSP Kitchener"]);
    gaps.push(["ODSP","Not confirmed","ODSP status and worker path unclear.","Confirm whether he has ODSP and who owns the file."]);
  }

  if(dsoMissing){
    steps.push(["2","Start or confirm DSO intake","DSO may be the key doorway to longer-term developmental-service supports.","Call DSO Central West and ask whether eligibility/application should be started or updated.","DSO Central West: 1-888-941-1121"]);
    gaps.push(["DSO","Not started / unclear","Developmental-service pathway may be missing.","Call DSO and ask what documentation is required."]);
  } else {
    steps.push(["2","Update DSO support profile","If DSO is already active, the support needs may need updating.","Ask DSO to capture employment, daily living, forms/calls, planning, education, and community support needs.","DSO Central West"]);
    gaps.push(["DSO",labelFor(a.dsoStatus),"Support profile may not reflect current needs.","Ask for review/update."]);
  }

  if(passportMissing){
    steps.push(["3","Check Passport funding","Passport may fund supports that short-term employment programs do not cover.","Ask DSO whether Passport is available, pending, or needs follow-up.","DSO Central West"]);
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
    steps.push(["5","Education repair path","College/training may have failed because formal supports were not in place.","Contact Conestoga Accessible Learning before re-enrolment and ask for documentation review and accommodation planning.","Conestoga Accessible Learning"]);
    gaps.push(["Education",labelFor(a.educationStatus),"Return path may fail again without accommodations.","Accessible Learning first, academic guidance second."]);
  } else {
    gaps.push(["Education",labelFor(a.educationStatus),"Not the immediate pathway unless he chooses it.","Keep as later goal."]);
  }

  if(docsWeak){
    steps.push(["6","Build document package","Applications and accommodations can stall without documentation.","Gather ODSP info, assessments, IEP/school records, college records, resume, and job-loss history.","Personal prep step"]);
    gaps.push(["Documentation","Limited or unclear","Records may not be ready for DSO, employment, or college supports.","Create one folder and one job-loss timeline."]);
  } else {
    gaps.push(["Documentation","Some records identified","Documents still need to be organized.","Create one folder and bring copies to calls."]);
  }

  steps.push(["7","Accommodation wording","Job and school supports work better when functional needs are clear.","Create a short list: what is hard, what helps, what support is needed, and what has failed before.","Employment advisor / Accessible Learning / HRLSC if needed"]);

  const pathwayBody = steps.map(s => row(s)).join("");
  byId("pathwayTable").querySelector("tbody").innerHTML = pathwayBody;
  byId("gapTable").querySelector("tbody").innerHTML = gaps.map(g => gapRow(g[0],g[1],g[2],g[3])).join("");

  const supportNeedText = a.supportNeeds.length ? a.supportNeeds.join(", ").replaceAll("_"," ") : "employment, job retention, forms, planning, and follow-through";
  const script = [
    "Call script:",
    "",
    "I am trying to connect with the right supports. The main issue is not just finding work; it is keeping work and having the right support after starting.",
    odspKnown ? "He is on or likely on ODSP, and we need to confirm what the ODSP worker can do for employment supports and job retention." : "ODSP status or worker information is unclear and needs to be confirmed.",
    dsoMissing ? "DSO status is not clear, so we need to know whether an application should be started." : "DSO may already be active, but the support profile may need to be updated.",
    passportMissing ? "Passport funding is not confirmed, so we need to ask whether it is available, pending, or possible." : "Passport funding may exist, so we need to know what employment or planning supports it can pay for.",
    "The support areas to capture are: " + supportNeedText + ".",
    "Please send the next steps in writing."
  ].join("\n");
  byId("generatedScript").textContent = script;

  plain.push("Current snapshot");
  plain.push("- ODSP: " + labelFor(a.odspStatus));
  plain.push("- ODSP worker known: " + labelFor(a.odspWorker));
  plain.push("- DSO: " + labelFor(a.dsoStatus));
  plain.push("- Passport: " + labelFor(a.passportStatus));
  plain.push("- Work pattern: " + labelFor(a.jobPattern));
  plain.push("- Education: " + labelFor(a.educationStatus));
  plain.push("");
  plain.push("First actions");
  steps.forEach(s => plain.push(`${s[0]}. ${s[1]} — ${s[3]} Contact: ${s[4]}.`));
  if(a.mainGoal){ plain.push(""); plain.push("Main goal: " + a.mainGoal); }
  if(a.contextNotes){ plain.push(""); plain.push("Context notes: " + a.contextNotes); }

  byId("plainTextPlan").textContent = plain.join("\n");
  byId("roadmapSummary").innerHTML = `<strong>Roadmap generated.</strong> The likely priority is: ${jobRetentionNeed ? "job-retention support plus ODSP/DSO/Passport coordination." : "confirming existing supports and building a structured employment/education plan."}`;
  updateDashboard();
  localStorage.setItem(storageKey, JSON.stringify(a));
  if(switchTab) goTab("roadmap");
}
