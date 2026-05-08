# Adds Contact Andrew to the Andrew D support roadmap navigation.
$repo = "C:\Users\andrew\PROJECTS\GitHub\my_git_documents"
Set-Location -LiteralPath $repo

$siteJs = Join-Path $repo "web\sites\andrewd\assets\site.js"
$content = Get-Content -LiteralPath $siteJs -Raw -Encoding UTF8

if ($content -notmatch "function addAndrewContactLink") {
    $content = $content -replace "addTodoLink\(\);", "addTodoLink(); addAndrewContactLink();"

    $function = @'

function addAndrewContactLink(){
  const nav = document.querySelector(".side-nav");
  if(nav && !nav.querySelector('a[href="contact_andrew.html"]')){
    nav.insertAdjacentHTML("beforeend", '<a class="nav-link" href="contact_andrew.html"><span class="nav-icon">🙋</span><span class="nav-text">Contact Andrew</span></a>');
  }
}
'@

    $content = $content.TrimEnd() + "`n" + $function + "`n"
    Set-Content -LiteralPath $siteJs -Value $content -Encoding UTF8
}

git status
git add web/sites/andrewd/contact_andrew.html web/sites/andrewd/assets/andrew_pearen_contact.vcf web/sites/andrewd/assets/site.js
git commit -m "Add Andrew follow-up contact options"
git push
