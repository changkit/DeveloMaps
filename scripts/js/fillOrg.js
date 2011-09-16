function setOrg(org) {
    var strorg = ""+org;
    document.getElementById(strorg).value = strorg;
}

function updateOrg(org) {
    document.getElementById("org_id").value = ""+org;
    document.getElementById("update_org_form").submit();
}