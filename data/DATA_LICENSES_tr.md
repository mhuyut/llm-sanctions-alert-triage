# Aday kamu veri setleri: lisans, boyut, indirilebilirlik

Kontrol tarihi: **2026-11-04**. Yöntem: yalnızca komut satırı (`curl -I`, en fazla birkaç KB'lık `curl -r 0-N` range isteği, FTP dizin listesi), WebFetch ve WebSearch. Tarayıcı kullanılmadı, hiçbir servise e-posta adresi gönderilmedi, büyük dosyaların hiçbiri tam indirilmedi. Boyutlar `Content-Length` / `Content-Range` başlıklarından ya da FTP listesinden alındı. Hesap açılmadı, Kaggle token'ı kullanılmadı.

> Bu bir lisans taramasıdır, hukuki görüş değildir. "Yeniden dağıtım" sütunu, kamuya açık bir GitHub replikasyon paketine **türetilmiş alt küme** konup konamayacağını gösterir.

## 1. Özet tablo

| # | Veri seti | Lisans / koşullar | Alt küme yeniden dağıtılabilir mi? | Boyut (başlıktan) | Format | Doğrudan URL (200/206 doğrulandı) | Ana tuzak |
|---|---|---|---|---|---|---|---|
| 1 | OFAC SDN (ABD Hazinesi) | ABD federal eseri, 17 U.S.C. §105 gereği telif yok (kamu malı) | **Evet** (telif açısından) | SDN.XML 29.3 MB · SDN_ADVANCED.XML 127.8 MB · SDN.CSV 5.75 MB · ALT.CSV 1.06 MB | XML / CSV | `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML` | HEAD 400 dönebiliyor (ALT/ADD); GET 302 ile 1 saatlik imzalı S3 URL'sine gidiyor. Gerçek kişilerin kişisel verisi |
| 2 | AB FSF konsolide liste | Komisyon yeniden kullanım bildirimi `COM_REUSE` (Karar 2011/833/AB): kaynak gösterilerek ticari ve ticari olmayan kullanım serbest | **Evet**, kaynak göstererek (kişisel veri çekincesiyle) | XML 25.9 MB · CSV 25.3 MB | XML / CSV (`;`) | `https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw` | Token herkese açık ve sabit (`dG9rZW4tMjAxNw` = base64 "token-2017"). Dosyanın generationDate'i 2026-10-23 (11 gün geride) |
| 3 | BM Güvenlik Konseyi konsolide listesi | un.org kullanım koşulları: yalnız "kişisel, ticari olmayan kullanım", yeniden dağıtım ve türev eser yasak | **Hayır** (yazılı izin gerekir) | 2.18 MB | XML | `https://scsanctions.un.org/resources/xml/en/consolidated.xml` (302 → Azure blob) | HEAD 404 dönüyor, GET çalışıyor. BM kayıtları AB/UK/OFAC listelerinde zaten var |
| 4 | UK Sanctions List (FCDO) | Open Government Licence v3.0, **ama OGL kişisel veriyi kapsamaz** | Kısmen: tüzel kişi ve gemi kayıtları evet; bireyler kişisel veri çekincesine tabi | CSV 50.4 MB · XML 22.1 MB · ODS 8.2 MB | CSV / XML / ODS / HTML / PDF | `https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml` | OFSI Consolidated List 28 Ocak 2026'da kapandı. Eski blob URL'si 409 dönüyor |
| 5 | OpenSanctions (`sanctions`, `default`) | CC BY-NC 4.0; işletmelerin lisans alması gerekiyor | Ticari olmayan akademik pakette **evet** (BY-NC, atıfla), ama paketin tamamı NC olur | sanctions: targets.simple.csv 78.8 MB, entities.ftm.json 381.6 MB · default: targets.simple.csv 473.5 MB, entities.ftm.json 2.58 GB | CSV / FtM JSONL | `https://data.opensanctions.org/datasets/latest/sanctions/targets.simple.csv` | Pairs (eşleştirme) veri setinin güncel sürümü token istiyor; eski pairs dosyası serbest |
| 6 | Türkiye MASAK / HMB malvarlığı dondurma listeleri | Açık lisans yok; RG'de yayımlanmış resmi kararlar (FSEK m.31). **KVKK: TCKN, anne ve baba adı içeriyor** | **Hayır** (kişisel veri: TCKN, anne ve baba adı) | A: docx 614 KB · B: xlsx 28 KB · C: xlsx 157 KB + csv 212 KB · D: xlsx 44 KB | DOCX / XLSX / CSV (cp1254, `;`) | `https://ms.hmb.gov.tr/uploads/sites/2/2026/10/C-IC-DONDURMA-...-951d1ad07e573d1e.csv` | Sayfa bir SPA (JS gerekiyor). Linkler WP API'den alınıyor, dosya adlarına hash ekleniyor, her güncellemede değişiyor |
| 7a | MIDV-500 (Smart Engines) | CC BY-SA 2.5 (ftp `license.txt`) | **Evet** (atıf + aynı lisans) | 50 zip × ~0.6–0.7 GB ≈ 33 GB | MOV/MP4 + TIF + JSON | `ftp://smartengines.com/midv-500/dataset/43_tur_id.zip` | **FTP'de yabancı dosyalar var (`Photo.scr`, `info.zip`, `test_write_perm_*`); bunlar açılmamalı** |
| 7b | MIDV-2020 | CC BY-SA 2.5 (**NC değil**); yüzler Generated Photos ile üretilmiş | **Evet** (atıf + aynı lisans) | templates.tar 863 MB · photo.tar 4.0 GB · scan_upright.tar 1.15 GB · clips.tar 10.3 GB · toplam ≈ 123 GB | JPG/TIF + VIA JSON | `ftp://smartengines.com/midv-2020/dataset/templates.tar` | Tüm alan değerleri sahte (mock). Anotasyonlar `templates.tar`'ın başında duruyor |
| 8 | IBM AMLworld (Altman vd. 2023) | CDLA-Sharing-1.0 | **Evet** (alt küme CDLA-Sharing altında yayımlanmalı; sonuçlar serbest) | Toplam 41.6 GB. HI-Small_Trans 475.7 MB · LI-Small_Trans 650.4 MB · HI-Medium 3.03 GB · LI-Medium 2.98 GB · HI-Large 17.05 GB · LI-Large 16.74 GB | CSV + Patterns.txt | `https://www.kaggle.com/api/v1/datasets/download/ealtman2019/ibm-transactions-for-anti-money-laundering-aml?fileName=HI-Small_Trans.csv` | Kaggle dışında güncel kopya yok (IBM Box linki 404) |
| 9 | PaySim (Kaggle ealaxi/paysim1) | CC BY-SA 4.0 | **Evet** (atıf + aynı lisans) | CSV 493.5 MB (zip 186.4 MB) | CSV | `https://www.kaggle.com/api/v1/datasets/download/ealaxi/paysim1` | Dolandırıcılık senaryosu; AML tipolojisi yok. Bakiye sütunlarında sızıntı var |
| 10 | SAML-D (Oztas vd. 2023) | CC BY-NC-SA 4.0 | **Evet**, ticari olmayan ve aynı lisansla | CSV 996.2 MB (zip 202.5 MB) | CSV | `https://www.kaggle.com/api/v1/datasets/download/berkanoztas/synthetic-transaction-monitoring-dataset-aml` | 28 tipoloji (11 normal + 17 şüpheli); şüpheli oranı %0.1039 |
| 11 | Sentetik KYC / SAR / adverse media | Karışık (aşağıda) | Kaynağa göre değişiyor | – | – | – | Olgun ve resmi bir "sentetik KYC müşteri profili" benchmark'ı bulunamadı |
| 12 | İsim / transliterasyon kaynakları | Wikidata CC0 · ParaNames (Wikidata türevi, repo MIT) · Dakshina CC BY-SA 4.0 · **JRC-Names EULA (türev ve dağıtım yasak)** | Wikidata / ParaNames / Dakshina: evet · JRC-Names: **hayır** | ParaNames 999 MB · Dakshina 2.0 GB · JRC entities.gzip 14.8 MB | TSV / TAR / gzip | `https://github.com/bltlab/paranames/releases/download/v2024.05.07.0/paranames.tsv.gz` | JRC-Names'in data.europa.eu kaydı ile EULA çelişiyor; ihtiyatlı yol EULA'ya uymak |

**Kaggle'a giriş gerekir mi?** Bugün **gerekmiyor**. `https://www.kaggle.com/api/v1/datasets/download/<owner>/<slug>[?fileName=...]` kimlik doğrulamasız GET isteğine 302 dönüyor ve imzalı bir `storage.googleapis.com` URL'sine yönlendiriyor (range isteğinde 206). Bunu üç veri setinde de doğruladım. `HEAD` isteği ise 404 dönüyor; bu yüzden doğrulama `GET -r 0-N` ile yapılmalı. Metadata uçları (`/api/v1/datasets/view/...`, `/api/v1/datasets/list/...`) da anonim çalışıyor. Bu davranış resmi olarak garanti edilmiyor; Kaggle anonim indirmeyi kapatırsa Mehmet'in kendi Kaggle API token'ını (`~/.kaggle/kaggle.json`) vermesi gerekir. Hesap açmadım.

---

## 2. Ayrıntılar

### 1. OFAC SDN listesi (ABD Hazinesi, Sanctions List Service)

- **Resmi kaynak:** https://sanctionslist.ofac.treas.gov/Home/SdnList (OFAC'ın hizmet sayfası: https://ofac.treasury.gov/sanctions-list-service)
- **Lisans:** OFAC sayfasında açık bir lisans cümlesi yok. ABD federal hükümet eseri olduğu için 17 U.S.C. §105 geçerli: *"Copyright protection under this title is not available for any work of the United States Government"*. data.gov kataloğunun SDN kaydında lisans "Creative Commons CCZero" görünüyor (WebSearch sonucuna göre; data.gov sayfası bugün 404 verdiği için doğrudan doğrulayamadım).
- **Yeniden dağıtım:** Telif açısından serbest. Kişisel veri ayrı bir konu (aşağıdaki "Genel uyarı" bölümüne bakın).
- **Dosyalar (GET range ile doğrulandı, Publish_Date 10/28/2026, Record_Count 19,484):**

  | Dosya | Bayt |
  |---|---|
  | `SDN.XML` | 29,271,441 |
  | `SDN_ADVANCED.XML` | 127,776,518 |
  | `SDN_ENHANCED.XML` | 110,007,882 |
  | `SDN.CSV` | 5,750,799 |
  | `ALT.CSV` (a.k.a. listesi) | 1,064,299 |
  | `ADD.CSV` | 1,690,668 |
  | `SDN_COMMENTS.CSV` | 48,137 |
  | `CONS_ADVANCED.XML` (non-SDN) | 4,580,537 |
  | `CONS_PRIM.CSV` | 268,508 |

  Taban URL: `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/<DOSYA>`. Eski `https://www.treasury.gov/ofac/downloads/sdn.xml` adresi de buraya 302 ile yönleniyor.
- **Yapı:**
  - `SDN.XML`: `sdnEntry{uid, firstName, lastName, sdnType, programList, akaList{aka{uid, type="a.k.a.", category="strong|weak", lastName, firstName}}, addressList, idList, dateOfBirthList, nationalityList…}`.
  - `ALT.CSV`: `ent_num, alt_num, alt_type("aka"/"fka"/"nka"), alt_name, remarks`, başlık satırı yok.
  - `SDN_ADVANCED.XML`: `ReferenceValueSets` içinde `AliasTypeValues` (A.K.A., F.K.A., N.K.A., Name) ve **`ScriptValues`** var: Arab, Armn, Hans, Hant, Cyrl, Geor, Grek, Hang, Hebrew, Japanese, Korean, Latin. İsim parçaları `ScriptID` ile etiketli, yani orijinal yazı sistemindeki isimler yalnızca ADVANCED formatta bulunuyor.
- **Tuzaklar:**
  - Sunucu `HEAD` isteğine bazı dosyalarda 400 dönüyor ve `Content-Length` göndermiyor. Boyut `GET -r 0-0` ile okunmalı.
  - İndirme 1 saat geçerli imzalı bir S3 (us-gov-west-1) URL'sine yönleniyor; kalıcı link olarak her zaman `exports/...` adresi kullanılmalı.
  - Liste sık güncelleniyor; makalede snapshot tarihi ve SHA-256 değeri sabitlenmeli.

### 2. AB Mali Yaptırımlar konsolide listesi (FSF, DG FISMA)

- **Resmi kaynak:** https://webgate.ec.europa.eu/fsd/fsf ; data.europa.eu kaydı: `consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions` (yayıncı: DG FISMA).
- **Lisans:** data.europa.eu API'sinde XML dağıtımının lisansı **`COM_REUSE`** olarak görünüyor (European Commission Reuse and Copyright Notice, https://data.jrc.ec.europa.eu/licence/com_reuse). Dayanağı Komisyon Kararı 2011/833/AB. Madde 3'e göre belgeler, Madde 6'daki koşullarla *"for commercial or non-commercial purposes"* ve ücretsiz olarak yeniden kullanılabilir. Madde 6'daki koşullar kaynak gösterme ve anlamı çarpıtmamadır. (Metin EUR-Lex'ten doğrudan çekilemedi, çünkü sunucu 202 ve boş gövde döndü; alıntı ikincil kaynaktan, nihai metinde https://eur-lex.europa.eu/eli/dec/2011/833/oj ile teyit edilmeli.) Kararın kapsamında kişisel veri korumasına ilişkin bir istisna bulunuyor (Madde 2).
- **Yeniden dağıtım:** Kaynak gösterilerek alt küme yayımlanabilir; bireylere ait kayıtlar kişisel veri çekincesine tabi.
- **Token sorusu:** Kamuya açık dosyalar `?token=dG9rZW4tMjAxNw` parametresi istiyor. Bu token herkese açık, sabit ve data.europa.eu'da da yayımlanmış durumda (base64 karşılığı "token-2017"). Kayıt gerekmiyor.
- **Dosyalar:**
  - XML 1.1: 25,899,600 B (`20261023-FULL-1_1(xsd).xml`)
  - CSV 1.1: 25,288,456 B (`20261023-FULL-1_1.csv`, `;` ayraçlı, UTF-8 BOM'lu)
  - URL'ler: `.../public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw` ve `.../public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw`
- **Yapı:** `export > sanctionEntity{euReferenceNumber, unitedNationId, logicalId, remark, regulation{programme, numberTitle, publicationUrl}, subjectType{code=person|enterprise}, nameAlias{firstName, middleName, lastName, wholeName, nameLanguage (ör. "FR"), strong, gender, function, title}, citizenship, birthdate, address, identification}`. CSV düzleştirilmiş: `Entity_*`, `NameAlias_*`, `Address_*`, `BirthDate_*`, `Identification_*`... sütunları ve takma ad başına bir satır.
- **Tuzaklar:**
  - zsh'de URL tırnak içine alınmalı, çünkü `?` karakteri glob olarak yorumlanıyor.
  - Bugün indirilen dosyanın `generationDate` değeri 2026-10-23. Public dosya her değişiklikte güncellenmeyebilir.
  - `europeaid/fsd/fsf` adresli eski kayıt artık DEPRECATED.

### 3. BM Güvenlik Konseyi Konsolide Listesi

- **Resmi kaynak:** https://main.un.org/securitycouncil/content/un-sc-consolidated-list (sayfada "last updated on 29 October 2026" yazıyor).
- **Lisans / koşullar:** https://www.un.org/en/about-us/terms-of-use adresindeki koşullara göre materyaller *"for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom"*. https://www.un.org/en/about-us/copyright sayfasında ise yayıncıdan yazılı izin isteniyor.
- **Yeniden dağıtım:** **Hayır** (UN Publications Rights & Permissions'tan yazılı izin alınması gerekir). Pratik çözüm: aynı BM kayıtları AB, UK ve OFAC listelerinde de yer alıyor. Pakete BM dosyası konmaz; yalnızca indirme script'i ve `DATAID` / `REFERENCE_NUMBER` listesi verilir.
- **Dosyalar:**
  - `https://scsanctions.un.org/resources/xml/en/consolidated.xml` (PRN sırası) ve `.../en/name/consolidated.xml` (alfabetik sıra).
  - Bu adresler 302 ile `unsolprodfiles.blob.core.windows.net/publiclegacyxmlfiles/EN/consolidatedLegacyByPRN.xml` dosyasına yönleniyor (SAS imzalı). Boyut 2,177,571 B, Last-Modified 2026-11-03.
  - SAS imzası olmadan blob'a doğrudan HEAD isteği de 200 döndü.
- **Yapı:** `CONSOLIDATED_LIST > INDIVIDUALS > INDIVIDUAL{DATAID, FIRST_NAME, SECOND_NAME, THIRD_NAME, UN_LIST_TYPE, REFERENCE_NUMBER, LISTED_ON, GENDER, COMMENTS1, NATIONALITY, INDIVIDUAL_ALIAS{QUALITY (Good/Low), ALIAS_NAME}, INDIVIDUAL_DATE_OF_BIRTH, INDIVIDUAL_DOCUMENT…}` ve `ENTITIES > ENTITY{…, ENTITY_ALIAS}`. Bazı kayıtlarda orijinal yazı sistemindeki isim ayrı bir alanda tutuluyor.
- **Tuzak:** `scsanctions.un.org` adresine `HEAD` isteği 404 dönüyor, `GET` isteği çalışıyor.

### 4. Birleşik Krallık: UK Sanctions List (FCDO), eski OFSI listesi

- **Resmi kaynak:** https://www.gov.uk/government/publications/the-uk-sanctions-list
- **Durum:** Sayfada *"The UK Sanctions List is now the only source for all UK sanctions designations."* ve *"The OFSI Consolidated List of Asset Freeze Targets closed on Wednesday 28 January 2026"* yazıyor. Eski `ofsistorage.blob.core.windows.net/.../ConList.csv` adresi artık 409 dönüyor ("Public access is not permitted").
- **Lisans:** Sayfada *"All content is available under the Open Government Licence v3.0"* deniyor. OGL v3 kopyalama, yayımlama, dağıtma, uyarlama ve *"exploit the Information commercially and non-commercially"* haklarını veriyor. Atıf şart: *"Contains public sector information licensed under the Open Government Licence v3.0."* **Ancak OGL'de "This licence does not cover: … personal data in the Information" ifadesi yer alıyor.** Yani bireylerin isimleri OGL kapsamı dışında; kişisel veri hukukuna (UK GDPR) tabi.
- **Dosyalar (HEAD 200, Last-Modified 2026-11-03):**
  - `https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.csv`: 50,354,956 B
  - `.../UK-Sanctions-List.xml`: 22,084,218 B
  - `.../UK-Sanctions-List.ods`: 8,151,041 B
  - Ayrıca `.odt`, `.html`, txt ve pdf sürümleri var.
- **Yapı (CSV, ilk satır "Report Date"):** `Last Updated, Unique ID, OFSI Group ID, UN Reference Number, Name 6, Name 1…Name 5, Name type (Primary Name/Alias), Alias strength, Title, **Name non-latin script, Non-latin script type, Non-latin script language**, Regime Name, Designation Type, Designation source, Sanctions Imposed, Other Information, UK Statement of Reasons, Address…, D.O.B, Nationality, National Identifier number, Passport number, Position, Gender, Town/Country of birth, Type of entity, …, IMO number, gemi alanları`. XML: `Designations > Designation{UniqueID, OFSIGroupID, UNReferenceNumber, Names{Name{Name6, NameType}}, …}`.
- **Artı:** Latin dışı yazı sistemindeki isim ve dil alanları açık sütunlar halinde verildiği için cross-script çiftleri doğrudan çıkarılabiliyor.

### 5. OpenSanctions

- **Resmi kaynak:** https://www.opensanctions.org/datasets/sanctions/ ve https://www.opensanctions.org/datasets/default/
- **Lisans:** Sitede *"The data is licensed under the terms of Creative Commons 4.0 Attribution NonCommercial"* ve *"Businesses must acquire a data license to use the dataset."* yazıyor. Muafiyet sayfasında (https://www.opensanctions.org/docs/commercial/exemption/) toplu veri ticari olmayan kullanım için kayıtsız ve API anahtarı olmadan indirilebiliyor. Verilen örnekler: "a student project, a hobby analysis, personal research". Ücretsiz API anahtarı kurumsal bağlantılı ve "studying sanctions policy, illicit finance, or related topics" alanında çalışan akademisyenlere veriliyor. Kâr amaçlı bir işletme içindeki her kullanım ve uyum taraması ticari sayılıyor.
- **Akademik kullanım:** Ücretsiz. Kâr amacı gütmeyen bir arXiv preprint'i ve kamuya açık bir paket BY-NC ile uyumlu. Ancak **paket NC lisansı devralır**. Mehmet'in bir bankadaki iş rolüyle karışırsa ticari kullanım sayılabilir; deney kişisel ve akademik çerçevede tutulmalı.
- **Boyutlar (HEAD, sürüm 2026-11-04):**

  | Koleksiyon | Varlık / hedef / kaynak | targets.simple.csv | entities.ftm.json | Diğer |
  |---|---|---|---|---|
  | `sanctions` | 309,879 / 74,180 / 94–96 kaynak | 78,790,802 B | 381,640,344 B | names.txt 11.7 MB, senzing.json 73.7 MB, targets.nested.json 443.8 MB |
  | `default` | 3,921,982 / 1,247,210 / 482 kaynak | 473,466,095 B | 2,580,242,906 B | statements.csv 8.79 GB, targets.nested.json 3.71 GB |

  URL kalıbı: `https://data.opensanctions.org/datasets/latest/<koleksiyon>/<dosya>`. Bu adres 307 ile tarihli artefakta yönleniyor; tekrarlanabilirlik için tarihli URL (`/artifacts/sanctions/20261104074704-gze/...`) kaydedilmeli.
- **targets.simple.csv sütunları:** `id, schema, name, aliases, birth_date, countries, addresses, identifiers, sanctions, phones, emails, program_ids, dataset, first_seen, last_seen, last_change`. Çok değerli alanlar `;` ile ayrılıyor. FtM JSON'da `properties.name`, `alias`, `weakAlias`, `previousName` ve her değerin kaynağı yer alıyor.
- **Türkiye alt veri seti `tr_fcib`:** "Türkiye Asset Freezing Sanctions List (MASAK)". 4,114 varlık, 2,283 hedef, günlük güncelleniyor. HMB'nin xlsx dosyalarını da yansıtıyor.
- **Eşleştirici açık kaynak yazılımlar:** `github.com/opensanctions/nomenklatura` ve `github.com/opensanctions/yente`; ikisi de MIT lisanslı (GitHub API ile doğrulandı). Yerelde çalıştırılabildikleri için veri dışarı gitmiyor.
- **İsim eşleştirme benchmark'ı (önemli):**
  - **OpenSanctions Pairs:** arXiv 2603.11051, NeurIPS 2026 D&B. 755,540 etiketli çift; makalede kural tabanlı üretim eşleştiricisi F1 %91.3, LLM'ler %98–99. LLM'lerin en çok cross-script transliterasyonda zorlandığı raporlanıyor. Bu, KYC/LLM makalesi için **doğrudan rakip ve kıyas noktası**.
  - Güncel "grouped pairs" (`https://delivery.opensanctions.com/licensed/pairs/latest/pairs.jsonl.gz`, yaklaşık 1M satır, aylık) için **data delivery token gerekiyor**.
  - Eski düz dosya **serbest**: `https://data.opensanctions.org/contrib/training/pairs-20251209.json.gz` (409,088,814 B, "non-commercial use"). Daha eski bir kopya: `.../contrib/training/pairs.json` (1,187,875,551 B, 2023). Her satırda `judgement` (positive/negative) ile `left` ve `right` FtM varlıkları var.
  - HF aynası: `sanctions-er-anon/opensanctions_pairs` (CC BY-NC 4.0, **gated**, HF hesabı ve onay istiyor).

### 6. Türkiye: MASAK / Hazine ve Maliye Bakanlığı malvarlığı dondurma listeleri

- **Resmi kaynak:** https://en.hmb.gov.tr/fcib-tf-current-list (İngilizce) ve masak.hmb.gov.tr. Site bir React SPA, curl çıktısında yalnızca "You need to enable JavaScript" metni görünüyor. **İçerik WordPress REST API üzerinden alınabiliyor:** `https://en.hmb.gov.tr/portal/v2/pages?slug=<slug>`. Slug'lar: `5madde_ing`, `6madde_ing`, `7madde_ing`, `3a3b`.
- **Makine okunabilir mi?** Kısmen. A listesi (6415 m.5, BMGK) yalnızca **DOCX**. B (m.6, yabancı ülke talepleri), C (m.7, iç dondurma kararları) ve D (7262 s. Kanun m.3.A/3.B, KİS finansmanı) listeleri **XLSX**, C listesi ayrıca **CSV**.

  | Liste | URL (2026-11-04 itibarıyla; hash'li dosya adı değişir) | Bayt | Last-Modified |
  |---|---|---|---|
  | A (m.5) | `https://ms.hmb.gov.tr/uploads/sites/2/2026/11/A-BIRLESMIS-MILLETLER-GUVENLIK-KONSEYI-KARARINA-ISTINADEN-MALVARLIKLARI-DONDURULANLAR-6415-SAYILI-KANUN-5.-MADDE-27.10-bd03e96c5f281433.docx` | 614,181 | 2026-11-02 |
  | B (m.6) | `https://ms.hmb.gov.tr/uploads/sites/2/2026/01/B-YABANCI-ULKE-TALEPLERINE-ISTINADEN-MALVARLIKLARI-DONDURULANLAR-6415-SAYILI-KANUN-6.-MADDE-972ff13d63fcaf1d.xlsx` | 28,110 | 2026-01-27 |
  | C (m.7) xlsx | `https://ms.hmb.gov.tr/uploads/sites/2/2026/10/C-IC-DONDURMA-KARARI-ILE-MALVARLIKLARI-DONDURULANLAR-6415-SAYILI-KANUN-7.-MADDE-01.10-0817bbc07093e95f.xlsx` | 156,635 | 2026-10-01 |
  | C (m.7) csv | `https://ms.hmb.gov.tr/uploads/sites/2/2026/10/C-IC-DONDURMA-KARARI-ILE-MALVARLIKLARI-DONDURULANLAR-6415-SAYILI-KANUN-7.-MADDE-01.10-951d1ad07e573d1e.csv` | 212,152 | 2026-10-01 |
  | D (7262 m.3.A/3.B) | `https://ms.hmb.gov.tr/uploads/sites/12/2026/07/D-7262-SAYILI-KANUN-3.A-VE-3.B-MADDELERI-EXCEL-29.07.2026-7065dd0684b9962c.xlsx` | 44,055 | 2026-07-29 |

- **Yapı (C csv, Windows-1254, `;` ayraçlı):** `SIRA NO; GERÇEK/TÜZEL KİŞİ/KURULUŞ/ORGANİZASYON ADI SOYADI ÜNVANI; KULLANDIĞI BİLİNEN DİĞER İSİMLER; TCKN/VKN/GKN/PASAPORT NO; UYRUĞU; MVD YAPTIRIM TÜRÜ; ANNE ADI; BABA ADI; DOĞUM TARİHİ/KURULUŞ; DOĞUM YERİ; ÖRGÜTÜ; KARAR TARİHİ-SAYISI; RESMİ GAZETE TARİHİ SAYISI; TABİ OLDUĞU DİĞER UYRUK`.
- **Lisans:** Açık bir veri lisansı yok. Kararlar Resmî Gazete'de yayımlanıyor. FSEK m.31, resmi olarak yayımlanmış mevzuat ve kararların çoğaltılmasını ve yayılmasını serbest bırakıyor (bu FSEK yorumu madde metnine bakılarak teyit edilmeli).
- **Yeniden dağıtım:** **Önerilmez.** Dosyalarda Türk vatandaşlarının **TCKN, anne ve baba adı, doğum yeri ve tarihi** var; bunlar KVKK kapsamında kişisel veri. Ayrıca C listesinin büyük bölümü iç terör soruşturmalarına (FETÖ/PDY vb.) ait, yani hassas bir küme. Kamu paketine yalnızca indirme script'i ve isteğe bağlı toplu istatistikler konmalı; ham satır ve TCKN konmamalı.
- **Tuzaklar:**
  - Dosya adlarına rastgele hash ekleniyor ve her güncellemede değişiyor. Kalıcı URL yok; script önce WP API'den güncel linki okumalı.
  - `ms.hmb.gov.tr` kök dizini 403 dönüyor, ama `/uploads/...` dosyaları 200 dönüyor.
  - Daha temiz bir alternatif: OpenSanctions `tr_fcib` (CC BY-NC; aynı kişisel veri çekincesi geçerli).

### 7. MIDV-500 ve MIDV-2020 (Smart Engines)

- **Resmi kaynak:** `ftp://smartengines.com/midv-500/` ve `ftp://smartengines.com/midv-2020/` (anonim FTP). Ayna: http://l3i-share.univ-lr.fr (MIDV-2020 için). Makaleler: MIDV-500, Computer Optics 43(5) 2019, doi 10.18287/2412-6179-2019-43-5-818-824; MIDV-2020, arXiv 2107.00396.
- **Lisans (FTP'deki `license.txt` dosyalarından okundu):**
  - MIDV-2020: *"This work is licensed under the Creative Commons Attribution-ShareAlike 2.5 Generic License."* Ek not: yüzler Generated Photos ile üretilmiş ve türev çalışmalarda Generated Photos'a atıf yapılması teşvik ediliyor. **Lisans CC BY-NC-SA değil, CC BY-SA 2.5.**
  - MIDV-500: aynı lisans, CC BY-SA 2.5. Readme'ye göre kaynak görüntüler *"either in public domain or distributed under public copyright licenses"* (Wikimedia Commons örnek belgeleri).
- **Yeniden dağıtım:** Evet; atıf ve aynı lisans (BY-SA 2.5) şartıyla alt küme (ör. seçilmiş görüntüler ve JSON) yayımlanabilir.
- **Sahte mi?** Evet. MIDV-2020'de 1000 adet *"mock identity documents, each with unique text field values and unique artificially generated faces"* var. MIDV-500'de 50 belge türünün Wikimedia örnek (specimen) görüntüleri kullanılmış; **`43_tur_id.zip` T.C. kimlik kartı örneği**.
- **MIDV-2020 boyutları (FTP listesi):**

  | Dosya | Bayt |
  |---|---|
  | `templates.tar` | 863,293,440 |
  | `photo.tar` | 4,002,467,840 |
  | `scan_upright.tar` | 1,149,143,040 |
  | `scan_rotated.tar` | 1,122,682,880 |
  | `scan_upright_tif.tar` | 26,121,226,240 |
  | `scan_rotated_tif.tar` | 26,121,226,240 |
  | `clips.tar` | 10,303,651,840 |
  | `clips_video.tar` | 53,746,647,040 |
  | Toplam | ≈ 123 GB |

  MD5 değerleri `md5.txt` dosyasında. 10 belge türü var: alb_id, aze_passport, esp_id, est_id, fin_id, grc_passport, lva_passport, rus_internalpassport, srb_passport, svk_id.
- **MIDV-500 boyutları:** 50 zip, her biri 600–695 MB (≈ 33 GB). Örnek: `ftp://smartengines.com/midv-500/dataset/43_tur_id.zip` (625,011,919 B). Ayrıca `pip install midv500` paketi mevcut.
- **Ground truth:**
  - MIDV-2020: VGG Image Annotator v2 JSON (`annotations/<CODE>.json`). Her `region` için `shape_attributes` (rect/quad) ve `region_attributes{field_name, value, features}` var. `alb_id` için alanlar: `photo, signature, authority, birth_date, birth_place, issue_date, expiry_date, gender, id_number, name, surname, nationality, number…`. Değerler UTF-8 ve sahte (ör. `"name": "Adnan"`, `"birth_date": "20-11-1991"`). **İpucu:** `templates.tar` dosyasında `annotations/` dizini en başta; `curl -r 0-<N>` ile yalnızca anotasyonları almak mümkün (`alb_id.json` ≈ 323 KB).
  - MIDV-500: `ground_truth/XX.json` içinde `{"field01": {"value": "...", "quad": [[x,y]×4]}, "photo": {...}}` yapısı ve kare başına belge köşe quad'ı var. Belge 18 (Arapça) ve 29 (Farsça) için değerler `"*"`.
- **⚠ GÜVENLİK UYARISI:** `ftp://smartengines.com/midv-500/` dizininde Smart Engines'e ait olmayan (farklı uid 109), 2026'da eklenmiş dosyalar var: **`Photo.scr` (Windows ekran koruyucu çalıştırılabilir dosyası, 60 KB), `info.zip` (3.5 MB), `2024833545.html`, `test_write_perm_8860/`**. Anonim yazma izninin kötüye kullanıldığı anlaşılıyor. Bu dosyalar **asla indirilmemeli veya açılmamalı**. Yalnızca `dataset/*.zip` indirilmeli ve MD5 değerleri `md5.txt` (2018 tarihli, uid 1000) ile ve mümkünse PyPI `midv500` paketindeki değerlerle karşılaştırılmalı.

### 8. IBM AMLworld (Altman vd., NeurIPS 2023 D&B, arXiv 2306.16424)

- **Resmi kaynak:** https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml. GitHub (https://github.com/IBM/AML-Data) yalnızca README ve LICENSE içeriyor, veri içermiyor. README'de *"Although this Github repository is under the Apache-2.0 license, the actual data is released under the CDLA-Sharing-1.0 license"* yazıyor. "Original data on Box" linki (`ibm.box.com/v/AML-Anti-Money-Laundering-Data`) artık **404**. Sonuç: **Kaggle dışında güncel bir resmi kopya yok.**
- **Lisans:** Community Data License Agreement – Sharing 1.0 (Kaggle metadata'sı ile doğrulandı). CDLA-Sharing §3.1(a): *"The Data (including the Enhanced Data) must be Published under this Agreement"*. §3.5: *"This Agreement imposes no obligations or restrictions on Your Use or Publication of Results."*
- **Yeniden dağıtım:** Evet; alt küme CDLA-Sharing-1.0 metniyle birlikte yayımlanmalı. Model çıktıları ve istatistikler serbest.
- **Dosyalar (Kaggle API, toplam 41,608,549,656 B):**

  | Varyant | `_Trans.csv` | `_accounts.csv` | `_Patterns.txt` |
  |---|---|---|---|
  | HI-Small | 475,664,283 | 34,053,187 | 323,844 |
  | LI-Small | 650,422,357 | 47,248,016 | 99,156 |
  | HI-Medium | 3,031,783,420 | 145,008,642 | 2,279,574 |
  | LI-Medium | 2,976,436,978 | 141,781,157 | 390,893 |
  | HI-Large | 17,052,760,651 | 147,691,860 | 13,807,473 |
  | LI-Large | 16,742,513,790 | 144,349,585 | 1,934,790 |

- **Yapı:**
  - `_Trans.csv`: `Timestamp, From Bank, Account, To Bank, Account, Amount Received, Receiving Currency, Amount Paid, Payment Currency, Payment Format, Is Laundering`. **İki sütunun adı da `Account`, okurken yeniden adlandırılmalı.**
  - `_accounts.csv`: `Bank Name, Bank ID, Account Number, Entity ID, Entity Name` (ör. "Corporation #33520").
  - `_Patterns.txt`: `BEGIN LAUNDERING ATTEMPT - FAN-OUT …` blokları (dosyada FAN-OUT doğrulandı). Makaledeki 8 desen: fan-out, fan-in, cycle, gather-scatter, scatter-gather, stack, bipartite, random; bu liste bellekten yazıldı, makaleden teyit edilmeli.
- **İndirme:** `https://www.kaggle.com/api/v1/datasets/download/ealtman2019/ibm-transactions-for-anti-money-laundering-aml?fileName=HI-Small_Trans.csv`. Anonim GET 302 → GCS ve range ile 206 doğrulandı. Tek dosya `fileName` ile **sıkıştırılmadan** iniyor.
- **İlgili:** HF `typhoon-ai/AMLworldCompactEval` (CDLA-Sharing-1.0 + MIT; AMLworld-Compact, arXiv 2610.13627). LLM değerlendirmesi için küçültülmüş HI-Small örneklemi; kıyas noktası olarak değerli.

### 9. PaySim (Kaggle ealaxi/paysim1)

- **Kaynak:** https://www.kaggle.com/datasets/ealaxi/paysim1 (E. Lopez-Rojas; doktora tezi http://urn.kb.se/resolve?urn=urn:nbn:se:bth-12932).
- **Lisans:** CC BY-SA 4.0 (Kaggle metadata). Yeniden dağıtım: evet, atıf ve aynı lisansla.
- **Boyut:** `PS_20174392719_1491204439457_log.csv` 493,534,783 B; Kaggle zip'i 186,385,561 B. Yaklaşık 6.36M satır, 744 adım (30 gün).
- **Sütunlar:** `step, type (CASH-IN/CASH-OUT/DEBIT/PAYMENT/TRANSFER), amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud`.
- **Tuzaklar:** Kaggle açıklamasına göre fraud işlemleri iptal edildiği için bakiye sütunları *"must not be used"* (etiket sızıntısı). Bu veri bir **hesap ele geçirme (ATO) dolandırıcılığı** senaryosu, AML tipolojisi değil. Gerçek bir Afrika mobil para servisinin agregat verisinden kalibre edilmiş.

### 10. SAML-D (Oztas vd., IEEE ICEBE 2023, doi 10.1109/ICEBE59045.2023.00028)

- **Kaynak:** https://www.kaggle.com/datasets/berkanoztas/synthetic-transaction-monitoring-dataset-aml
- **Lisans:** CC BY-NC-SA 4.0 (Kaggle metadata). Yeniden dağıtım: ticari olmayan amaçla, atıf ve aynı lisansla evet.
- **Boyut:** `SAML-D.csv` 996,168,850 B; zip 202,528,964 B. 9,504,852 işlem, %0.1039 şüpheli.
- **Sütunlar (12):** `Time, Date, Sender_account, Receiver_account, Amount, Payment_currency, Received_currency, Sender_bank_location, Receiver_bank_location, Payment_type, Is_laundering, Laundering_type`. Bu adlar Kaggle açıklamasındaki özellik listesi ve makaleye dayanıyor; CSV zip içinde olduğu için başlık satırı range isteğiyle okunamadı, ilk okumada teyit edilmeli.
- **Tipoloji etiketleri:** 28 tipoloji (11 normal + 17 şüpheli), 15 ağ yapısı. Yüksek riskli lokasyonlar arasında Meksika, **Türkiye**, Fas ve BAE var. Kaggle'daki sürüm makaledekinden daha yeni.

### 11. Sentetik KYC / müşteri profili / SAR / adverse media kaynakları

Olgun ve yaygın kabul görmüş bir "sentetik KYC müşteri profili" benchmark'ı **bulunamadı**. arXiv 2512.06240 da "no public benchmark datasets exist" diyor. Bulunanlar:

| Kaynak | Ne | Lisans | Not |
|---|---|---|---|
| **Feedzai BAF**: Kaggle `sgpjesus/bank-account-fraud-dataset-neurips-2022` | Sentetik **banka hesabı açılış başvuruları** (onboarding/KYC dolandırıcılığı); Base + 5 bias varyantı | CC BY-NC-SA 4.0 | 6 CSV, toplam 1.36 GB (her biri 213–252 MB). KYC'ye en yakın tablo veri; anonim Kaggle indirmesi çalışıyor |
| **IDNet** (Zenodo, 8 parça) | Sentetik kimlik belgeleri + sahtecilik varyantları (MIDV-2020 türleri dahil: ALB, AZE, EST, FIN, GRC, LVA, RUS, SRB, SVK ve ABD eyaletleri) | **CC0** | Toplam ≈ 387 GB. Ör. part 1: https://doi.org/10.5281/zenodo.13854897 |
| **gretelai/synthetic_pii_finance_multilingual** (HF) | Sentetik finansal belgeler (sözleşme, form vb.) ve PII span'leri; çok dilli | Apache-2.0 | HF etiketi 10K–100K kayıt, parquet. KYC belge çıkarımı ve PII için kullanılabilir |
| **VynFi/vynfi-sar-narratives** (HF) | 156,787 sentetik işlem + AML etiketleri + **SAR narrative** metni | Apache-2.0 | Tek geliştiricinin aracı (DataSynth); kalitesi doğrulanmadı |
| **Webz.io Adverse Media** (HF `rangeva/adverse-media-dataset` → GitHub `Webhose/adverse-media-dataset`) | Negatif duygulu finans haberleri (gerçek haber metni) | "other": Webz.io ToU, *"free for academic, research, and journalistic purposes"* | Gerçek kişileri içeriyor ve etiketler otomatik; kamu paketine metin konmamalı, yalnızca ID verilmeli |
| **Elliptic** (Kaggle `ellipticco/elliptic-data-set`) | Bitcoin işlem grafiği, illicit/licit etiketli | **CC BY-NC-ND 4.0** | **ND (türev yasak)**, alt küme yayımlanamaz |
| **GROGU-KYC** (IEEE DataPort) | 10K sentetik PDF (maaş bordrosu, fatura, ekstre…) ve sahtecilik etiketleri | Belirtilmemiş, abonelik | Kullanılmaması önerilir |
| UniDataPro / UniqueData "KYC photo" (HF) | Gerçek insan fotoğrafları | CC BY-NC-ND 4.0 | ND ve biyometrik veri: **kullanılmamalı** |

FinCEN'in kamuya açık sentetik bir SAR narrative seti bulunamadı. FinCEN yalnızca agregat SAR istatistikleri yayımlıyor.

### 12. İsim varyantı / transliterasyon kaynakları (hard negative üretmek için)

| Kaynak | Lisans (alıntı / kaynak) | Boyut / URL | Uygunluk |
|---|---|---|---|
| **Wikidata** | https://www.wikidata.org/wiki/Wikidata:Licensing: yapılandırılmış veri (main, Property, Lexeme, EntitySchema) *"released into the public domain under Creative Commons Zero"* | `latest-truthy.nt.bz2` 43.6 GB, `latest-all.json.bz2` 103.6 GB (dumps.wikimedia.org, HEAD 200). Pratikte SPARQL (query.wikidata.org) ile P31=Q5 ve çok dilli `rdfs:label`/`skos:altLabel` sorgulamak daha uygun | **En temiz kaynak.** Ancak gerçek kişi isimleri; yalnızca isim dizgeleri kullanılmalı, kişi eşlemesi yapılmamalı |
| **ParaNames** (Sälevä & Lignos, LREC-COLING 2024) | Wikidata'dan türetilmiş (CC0); repo lisansı MIT. README'de ayrı bir veri lisansı yok | `https://github.com/bltlab/paranames/releases/download/v2024.05.07.0/paranames.tsv.gz` (999,401,108 B, HEAD 200). Sütunlar: `wikidata_id, eng, label, language, type (PER/LOC/ORG)`, 16.8M varlık, 400+ dil | **Çok uygun.** Hazır PER çiftleri (Latin ↔ Arapça/Kiril/Çince…) içeriyor |
| **Dakshina** (Google Research) | *"The dataset is licensed under CC BY-SA 4.0"* | `https://storage.googleapis.com/gresearch/dakshina/dakshina_dataset_v1.0.tar` (2,008,340,480 B) | Yalnızca 12 Güney Asya dili ve kelime düzeyinde romanizasyon; isim odaklı değil, sınırlı fayda |
| **JRC-Names** (AB JRC) | EULA (`https://wt-public.emm4u.eu/Resources/LICENCE-EULA_JRC-Names_2011.pdf`, okundu): *"personal, non-exclusive and royalty-free licence to Use"*; m.2.3 alt lisans ve devri, m.2.4 *"create derivative works … or copy"* eylemlerini yasaklıyor | `https://wt-public.emm4u.eu/data/entities.gzip` (14,843,240 B, 2024-03-15) | **Pakete konamaz.** Yalnızca yerel deneyde kullanılabilir; data.europa.eu RDF kaydı COM_REUSE gösterse bile EULA'ya uyulmalı |
| OpenSanctions Pairs (bkz. §5) | CC BY-NC 4.0 | 409 MB (eski) | Gerçek analist kararları; cross-script negatifler içeriyor |
| UK Sanctions List "Name non-latin script" sütunları ve OFAC ADVANCED `ScriptID` (bkz. §1, §4) | OGL / kamu malı | – | Listelerin kendi içinden cross-script pozitif çiftler |

---

## 3. Genel uyarı: yaptırım listelerinde kişisel veri

Yaptırım listeleri gerçek kişilerin adını, doğum tarihini ve pasaport numarasını içeriyor. Bunlar kamuya açık olsa da kişisel veri sayılıyor (GDPR / UK GDPR / KVKK). OGL bu veriyi açıkça kapsam dışında bırakıyor; BM koşulları yeniden dağıtımı zaten yasaklıyor. Replikasyon paketi için önerilen yapı:

1. **Ham liste kopyası konmamalı.** Yerine `scripts/fetch_*.py` (tarihli URL, SHA-256, indirme tarihi) konmalı.
2. Değerlendirme setinde **liste kimlikleri** (OFAC `uid`, EU `logicalId`, UK `Unique ID`, OpenSanctions `id`) ve **sentetik sorgu varyantları** (yazım hatası, transliterasyon, kelime sırası) tutulmalı. Sorgu isimleri sentetik üretildiği için paket gerçek kişi verisi taşımaz.
3. Gerçek isim gösterilmesi gerekiyorsa tercihen tüzel kişi ve gemi kayıtları ya da OFAC (ABD kamu malı) kullanılmalı.
4. Türkiye listeleri (TCKN, anne ve baba adı) hiçbir biçimde pakete konmamalı.

## 4. Öneri (hangi veri ne için)

- **(a) Yaptırım isim taraması:** Ana kaynak **OFAC SDN_ADVANCED.XML** (kamu malı, script etiketli takma adlar) + **UK Sanctions List CSV** (OGL, Latin dışı isim sütunları). Hard negatifler için **ParaNames/Wikidata (CC0)**. **OpenSanctions Pairs**, BY-NC'yi kabul ediyorsak ikincil bir benchmark olarak eklenir. EU FSF (COM_REUSE) üçüncü kaynak olabilir. BM ve JRC-Names yalnızca yerel olarak kullanılmalı.
- **(b) Kimlik belgesi alan çıkarımı:** **MIDV-2020** (CC BY-SA 2.5, tamamen sahte değerler, VIA JSON alan değerleri; önce yalnızca `templates.tar` ve `photo.tar`, ≈ 4.9 GB). Türk kimlik kartı için MIDV-500 `43_tur_id.zip`. Sahtecilik ve ölçek için IDNet (CC0). FTP'deki yabancı dosyalara dokunulmamalı.
- **(c) İşlem izleme:** **IBM AMLworld HI-Small / LI-Small** (CDLA-Sharing, en temiz paylaşım koşulları, tipoloji desenleri). İkinci veri olarak **SAML-D** (BY-NC-SA, 28 tipoloji). PaySim yalnızca dolandırıcılık kıyası için kullanılmalı; Elliptic ND olduğu için kullanılmamalı.
