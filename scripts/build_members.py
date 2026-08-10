import json, os, urllib.request

members_raw = [
 {"name":"ഗീത വി കെ","role":"Welfare Standing Committee Member","ward":1,"wardMl":"നീർണ്ണമുക്ക്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/ad9a8043-6013-45b7-913a-8bbaf2a399e2.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"പി സി ശിവകുമാർ","role":"Health and Education Standing Committee Member","ward":2,"wardMl":"കല്ലംപറമ്പ്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/8d9b64ad-b218-4bc7-a52a-af3129b1a36f.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"അഖില സി യു","role":"Development Standing Committee Chairman","ward":3,"wardMl":"കുന്നത്തറ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/dc91e5c7-535d-41b1-966c-27762cb7c4b1.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"ഹരിദാസൻ പി സി","role":"Development Standing Committee Member","ward":4,"wardMl":"കോടത്തൂർ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/4a4290ce-19f3-480b-b585-3f9eb059afd6.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"സഞ്ജിത് എം","role":"Finance Standing Committee member","ward":5,"wardMl":"ചെറുകര","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/19597f56-7e8a-465c-9c67-a6526b8730cf.JPG/10132100738","party":"Bharatiya Janata Party"},
 {"name":"സജിത എം","role":"President","ward":6,"wardMl":"കല്ലേപ്പാടം","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/e7820ff3-1e62-451d-960b-001883da951d.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"ലേഖാമണി ടി","role":"Finance Standing Committee member","ward":7,"wardMl":"പാറക്കൽ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/55c73578-1d1f-44a2-864a-9d3a84fa3326.JPG/10132100738","party":"Indian National Congress"},
 {"name":"പ്രിയ വി സി","role":"Health and Education Standing Committee Member","ward":8,"wardMl":"കുന്നംപുള്ളി","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/5246cb24-c462-4111-8246-c68ad2ffbff2.JPG/10132100738","party":"Indian National Congress"},
 {"name":"ഷിഫാനത്ത് യു എച്ച്","role":"Development Standing Committee Member","ward":9,"wardMl":"പൊറ്റ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/c12f479d-7609-477b-9e84-0fd4b90bb1d0.JPG/10132100738","party":"Indian National Congress"},
 {"name":"മുഹമ്മദ് മുസ്തഫ പി എ","role":"Welfare Standing Committee Member","ward":10,"wardMl":"വെന്നൂർ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/c5a0e60a-a020-430f-88f6-14b09bd29e1a.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"രാജീവ് കെ എസ്","role":"Development Standing Committee Member","ward":11,"wardMl":"അടിച്ചിറ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/5f543415-b5f7-49ce-aecf-25fc7d893b82.JPG/10132100738","party":"Indian National Congress"},
 {"name":"സജി കെ വി","role":"Development Standing Committee Member","ward":12,"wardMl":"തിരുമണി","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/81593121-2921-4c36-8db2-8fd2c24f5cb1.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"അനു ടി പി","role":"Finance Standing Committee member","ward":13,"wardMl":"എളനാട്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/862f0348-30c6-4b46-ac58-fced04834084.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"നിർമ്മല ടി","role":"Health and Education Standing Committee Chairman","ward":14,"wardMl":"നീളംപള്ളിയാൽ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/20c44d9c-aa1b-4dd4-a74d-0e2f9094ca48.JPG/10132100738","party":"Indian National Congress"},
 {"name":"സുരേഷ് സി സി","role":"Vice President & Chairman Standing Committee for Finance","ward":15,"wardMl":"തൃക്കണായ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/ac16a657-c4fe-4be7-ac67-361a24ffdbde.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"സുബൈദ യു","role":"Finance Standing Committee member","ward":16,"wardMl":"പരുത്തിപ്ര","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/c5c0dadb-bfa1-4387-8718-67ff37d28e6b.JPG/10132100738","party":"Indian National Congress"},
 {"name":"പ്രമീള ബി","role":"Welfare Standing Committee Member","ward":17,"wardMl":"വെണ്ടോക്കുംപറമ്പ്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/caf9e1fa-22d7-41a5-bf5d-c807f636ffc1.JPG/10132100738","party":"Indian National Congress"},
 {"name":"ശ്രീമതി","role":"Health and Education Standing Committee Member","ward":18,"wardMl":"കുമ്പളക്കോട്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/8724b786-279e-4634-8bde-3a72de798f72.JPG/10132100738","party":"Indian National Congress"},
 {"name":"സിജി ജോൺ","role":"Welfare Standing Committee Chairman","ward":19,"wardMl":"വെളളപ്പാറ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/96cd130c-2249-4490-923b-646330c2336f.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"ബാബു എൻ","role":"Health and Education Standing Committee Member","ward":20,"wardMl":"പഴയന്നൂർ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/f7fac650-b88b-4079-b12e-3765ff3e9ca3.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"വിനോദിനി എ ജി","role":"Welfare Standing Committee Member","ward":21,"wardMl":"അത്താണിപറമ്പ്","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/adc8fc48-8b72-427c-a5e4-6a91f538826b.JPG/10132100738","party":"Indian National Congress"},
 {"name":"ദിൽഷാദ് നിസാം ഐ","role":"Finance Standing Committee member","ward":22,"wardMl":"വെള്ളാർകുളം","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/aac8cd1c-d96d-49a2-bf55-7b72d2ea0c48.JPG/10132100738","party":"Communist Party of India (Marxist)"},
 {"name":"കൃഷ്ണകുമാർ പി","role":"Development Standing Committee Member","ward":23,"wardMl":"പുത്തിരിത്തറ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/211e2a02-2644-4c53-abc5-81688df76e9e.JPG/10132100738","party":"Bharatiya Janata Party"},
 {"name":"മനോജ് എം","role":"Welfare Standing Committee Member","ward":24,"wardMl":"വടക്കേത്തറ","photo":"https://api.ksmart.lsgkerala.gov.in/meeting-management-services/auth/pdf/fetch-member-photo/6de122b5-f8c9-4e27-b4a0-19cddc5d632b.jpg/10132100738","party":"Bharatiya Janata Party"},
]

role_en_map = {
    "President": ("President", "പ്രസിഡന്റ്"),
    "Vice President & Chairman Standing Committee for Finance": ("Vice President & Finance Standing Committee Chairman", "വൈസ് പ്രസിഡന്റ് & ധനകാര്യ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി ചെയർമാൻ"),
    "Development Standing Committee Chairman": ("Development Standing Committee Chairman", "വികസന സ്റ്റാൻഡിംഗ് കമ്മിറ്റി ചെയർമാൻ"),
    "Welfare Standing Committee Chairman": ("Welfare Standing Committee Chairman", "ക്ഷേമകാര്യ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി ചെയർമാൻ"),
    "Health and Education Standing Committee Chairman": ("Health & Education Standing Committee Chairman", "ആരോഗ്യ-വിദ്യാഭ്യാസ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി ചെയർമാൻ"),
    "Welfare Standing Committee Member": ("Welfare Standing Committee Member", "ക്ഷേമകാര്യ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി അംഗം"),
    "Health and Education Standing Committee Member": ("Health & Education Standing Committee Member", "ആരോഗ്യ-വിദ്യാഭ്യാസ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി അംഗം"),
    "Development Standing Committee Member": ("Development Standing Committee Member", "വികസന സ്റ്റാൻഡിംഗ് കമ്മിറ്റി അംഗം"),
    "Finance Standing Committee member": ("Finance Standing Committee Member", "ധനകാര്യ സ്റ്റാൻഡിംഗ് കമ്മിറ്റി അംഗം"),
}

party_short = {
    "Communist Party of India (Marxist)": "CPI(M)",
    "Indian National Congress": "INC",
    "Bharatiya Janata Party": "BJP",
}

out = []
for m in members_raw:
    fname = f"ward-{m['ward']:02d}.jpg"
    dest = f"D:/pazhayannur.com/src/assets/administration/members/{fname}"
    req = urllib.request.Request(m["photo"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    role_en, role_ml = role_en_map.get(m["role"], (m["role"], m["role"]))
    out.append({
        "ward": m["ward"],
        "wardMl": m["wardMl"],
        "name": m["name"],
        "role": role_en,
        "roleMl": role_ml,
        "party": party_short.get(m["party"], m["party"]),
        "partyFull": m["party"],
        "image": f"../assets/administration/members/{fname}",
    })
    print("downloaded", fname, os.path.getsize(dest), "bytes")

with open("D:/pazhayannur.com/src/data/members.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("done, total members:", len(out))
