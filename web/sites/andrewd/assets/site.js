
const fields = ["q_odsp","q_worker","q_jobs","q_dso","q_assessment","q_passport","q_college","q_accom","q_overwhelm","notes"];

function isChecked(id){ return document.getElementById(id)?.checked === true; }

function add(line, out){ out.push(line); }

function generatePlan(){
  const out = [];
  const notes = document.getElementById("notes").value.trim();

  add("ANDREW D SUPPORT ACTION PLAN", out);
  add("=============================", out);
  add("", out);

  add("1. First contact", out);
  if(isChecked("q_odsp")){
    add("- Call ODSP Kitchener: 519-886-4700.", out);
    add("- Ask for ODSP Employment Supports, job-retention support, service-provider referral, and written next steps.", out);
    if(!isChecked("q_worker")) add("- Ask ODSP to identify the assigned worker or correct contact person.", out);
  } else {
    add("- Call 211 and ask how to confirm ODSP status or start support navigation.", out);
  }

  add("", out);
  add("2. DSO / Passport path", out);
  if(isChecked("q_dso")){
    add("- Call DSO Central West: 1-888-941-1121.", out);
    add("- Ask to review or update the support profile so all needs are captured.", out);
  } else {
    add("- Call DSO Central West: 1-888-941-1121.", out);
    add("- Ask whether a DSO eligibility application should be started.", out);
  }
  if(isChecked("q_assessment")){
    add("- Gather psychological, school, learning, disability, IEP, or accommodation records before intake.", out);
  } else {
    add("- Ask DSO what options exist if no psychological assessment is available.", out);
  }
  if(isChecked("q_passport")){
    add("- Ask KW Habilitation whether Passport can pay for KW Career Compass, job coaching, or person-directed planning.", out);
  } else {
    add("- Ask DSO whether Passport eligibility or funding is available or pending.", out);
  }

  add("", out);
  add("3. Employment stability", out);
  if(isChecked("q_jobs")){
    add("- Contact KW Career Compass: 519-744-6307.", out);
    add("- Contact Starling Employment Services: 519-743-2460.", out);
    add("- Say clearly: the main issue is keeping work after starting, not only finding work.", out);
    add("- Ask for job coaching, on-the-job training, job-retention follow-up, and employer-support planning.", out);
  } else {
    add("- Ask an employment advisor for job matching, skills assessment, and career planning before applying widely.", out);
  }

  add("", out);
  add("4. Accommodation support", out);
  if(isChecked("q_accom") || isChecked("q_jobs")){
    add("- Prepare a simple functional-needs list: what is hard, what helps, and what support is needed.", out);
    add("- If disability-related accommodation may have been ignored, contact the Human Rights Legal Support Centre: 1-866-625-5179.", out);
  } else {
    add("- Keep accommodation information ready in case work or school barriers appear.", out);
  }

  add("", out);
  add("5. Education return path", out);
  if(isChecked("q_college")){
    add("- Contact Conestoga Accessible Learning: accessibility@conestogac.on.ca or 519-748-5220 ext. 3232.", out);
    add("- Complete the intake form before returning to classes.", out);
    add("- Ask for documentation review, accommodations, and a realistic re-entry plan.", out);
  } else {
    add("- If school becomes a goal, contact Accessible Learning before applying or registering.", out);
  }

  add("", out);
  add("6. Support method", out);
  if(isChecked("q_overwhelm")){
    add("- Ask every organization to send next steps in writing.", out);
    add("- Use one folder for letters, forms, worker names, phone numbers, appointments, and deadlines.", out);
    add("- Bring a trusted support person to calls or meetings where allowed.", out);
  } else {
    add("- Keep a simple contact log: date, organization, person, next step, deadline.", out);
  }

  if(notes){
    add("", out);
    add("Personal notes", out);
    notes.split(/\n+/).forEach(n => add("- " + n, out));
  }

  document.getElementById("planOutput").textContent = out.join("\n");
}

function saveAnswers(){
  const data = {};
  fields.forEach(id => {
    const el = document.getElementById(id);
    if(!el) return;
    data[id] = el.type === "checkbox" ? el.checked : el.value;
  });
  localStorage.setItem("andrewdSupportRoadmap", JSON.stringify(data));
  generatePlan();
}

function loadAnswers(){
  const raw = localStorage.getItem("andrewdSupportRoadmap");
  if(!raw){
    document.getElementById("planOutput").textContent = "No saved answers found on this browser.";
    return;
  }
  const data = JSON.parse(raw);
  fields.forEach(id => {
    const el = document.getElementById(id);
    if(!el || !(id in data)) return;
    if(el.type === "checkbox") el.checked = data[id];
    else el.value = data[id];
  });
  generatePlan();
}
