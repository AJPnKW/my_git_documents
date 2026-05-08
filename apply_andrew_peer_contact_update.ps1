# Apply Andrew P peer contact page to Andrew D support roadmap.
$repo = "C:\Users\andrew\PROJECTS\GitHub\my_git_documents"
Set-Location -LiteralPath $repo

$siteJs = Join-Path $repo "web\sites\andrewd\assets\site.js"
$content = Get-Content -LiteralPath $siteJs -Raw -Encoding UTF8

# Ensure Contact Andrew P appears in the left menu.
if ($content -notmatch "function addAndrewContactLink") {
    $content = $content -replace "addTodoLink\(\);", "addTodoLink(); addAndrewContactLink();"

    $function = @'

function addAndrewContactLink(){
  const nav = document.querySelector(".side-nav");
  if(nav && !nav.querySelector('a[href="contact_andrew.html"]')){
    nav.insertAdjacentHTML("beforeend", '<a class="nav-link" href="contact_andrew.html"><span class="nav-icon">🙋</span><span class="nav-text">Contact Andrew P</span></a>');
  }
}
'@
    $content = $content.TrimEnd() + "`n" + $function + "`n"
} else {
    $content = $content -replace "Contact Andrew</span>", "Contact Andrew P</span>"
}

# Rename the support-organization contact block so it does not sound like Andrew P's contact card.
$content = $content -replace "📇 Add support contacts", "📇 Add organization contacts"
$content = $content -replace "Download a contact file and open it on your phone or computer to add these support organizations to your contacts\.", "Download a contact file for ODSP, DSO, employment, Conestoga, and other support organizations."
$content = $content -replace "Add contacts file", "Add organization contacts"

Set-Content -LiteralPath $siteJs -Value $content -Encoding UTF8

git status
git add web/sites/andrewd/contact_andrew.html web/sites/andrewd/assets/andrew_pearen_contact.vcf web/sites/andrewd/assets/site.js
git commit -m "Add Andrew P peer contact page"
git push
