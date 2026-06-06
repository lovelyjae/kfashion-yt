# 📊 BUYMA 재고·마진 관리 시트 + 매일 자동 재고체크

> 2026-06-07 · `product/buyma_inventory_template.csv`를 Google Sheets로 임포트하면 **마진 자동계산** + **재고 자동알림**까지.
> 핵심 답: **"오래된 행 자동 알림"은 100% 가능. "품절 자동 감지"는 사이트에 따라 부분 가능**(아래 한계 참고).

---

## 1. 임포트 방법 (2분)
1. Google Sheets 새 시트 → **파일 → 가져오기 → 업로드** → `buyma_inventory_template.csv`
2. 가져오기 위치: **현재 시트 바꾸기**, 구분자 **쉼표**, **"텍스트를 숫자·날짜·수식으로 변환" 체크 ✅** (수식이 살아남)
3. 끝. J~O, S, T 열은 **자동 계산**됨. 행 추가 시 J2:T2를 아래로 채우기(fill down).

## 2. 열 구조 (입력 vs 자동)
| 열 | 항목 | 종류 |
|---|---|---|
| A | 관리번호 | 입력 |
| B | 브랜드 | 입력 |
| C | 商品名(JP 타이틀) | 입력 |
| D | 商品紹介(짧게) | 입력 |
| E | 컬러 옵션 | 입력 |
| F | 仕入価格(₩) | 입력 |
| G | 国際送料(¥) | 입력 |
| H | 目標利益(¥) | 입력 |
| I | 為替(₩/¥) | 입력(기본 9.3, 수시 갱신) |
| **J** | 原価(¥) | **자동** `=F/I+G` |
| **K** | 販売価格(¥) | **자동** `=(J+H)/0.903` (10엔 반올림) |
| **L** | 課税価格(¥) | **자동** `=K*0.6` |
| **M** | 免税判定 | **자동** `<¥10,000 → 免税` |
| **N** | 実利益(¥) | **자동** `=K-J-K*0.077-K*0.02` (수수료7.7%+환손2%) |
| **O** | 利益率(%) | **자동** |
| P | **仕入先URL** | 입력 ← 추가 요청 열 |
| Q | **最近確認日** | 입력/스크립트 자동갱신 ← 추가 요청 열 |
| R | 在庫状態 | 스크립트 자동/수동 (在庫OK·品切れ·要確認) |
| **S** | 経過日 | **자동** `=TODAY()-Q` |
| **T** | アラート | **자동** `경과 3일↑ → 要確認` |

> 마진식은 11번 문서와 동일. 환율(I)만 가끔 갱신하면 전 행 판매가·이익 재계산.

---

## 3. 매일 자동 재고체크 (Google Apps Script)

**확장프로그램 → Apps Script**에 아래 붙여넣고 저장 → `setupDailyTrigger` 1회 실행(권한 허용) → **매일 자동 실행**.

```javascript
// === BUYMA 재고 자동체크 (매일) ===
const COL = { URL: 16, CHECKED: 17, STATUS: 18 }; // P=16, Q=17, R=18
const SOLDOUT_WORDS = ['품절','sold out','soldout','품 절','매진','在庫なし','SOLD OUT','일시품절','재입고'];
const STALE_DAYS = 3;

function checkStockDaily() {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const last = sh.getLastRow();
  const today = new Date();
  const alerts = [];

  for (let r = 2; r <= last; r++) {
    const url = sh.getRange(r, COL.URL).getValue();
    if (!url || String(url).indexOf('example.com') > -1) continue; // 미입력/샘플 스킵

    let status = '要確認';
    try {
      const res = UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true,
        headers: { 'User-Agent': 'Mozilla/5.0' } });
      const code = res.getResponseCode();
      if (code >= 200 && code < 400) {
        const html = res.getContentText().toLowerCase();
        const sold = SOLDOUT_WORDS.some(w => html.indexOf(w.toLowerCase()) > -1);
        status = sold ? '品切れ' : '在庫OK';
      } else {
        status = '要確認(HTTP ' + code + ')';
      }
    } catch (e) {
      status = '要確認(取得失敗)';
    }

    sh.getRange(r, COL.STATUS).setValue(status);              // R: 在庫状態
    sh.getRange(r, COL.CHECKED).setValue(today);              // Q: 最近確認日 갱신
    if (status.indexOf('品切れ') > -1 || status.indexOf('要確認') > -1) {
      alerts.push(`${sh.getRange(r,2).getValue()} / ${sh.getRange(r,3).getValue()} → ${status}`);
    }
    Utilities.sleep(1500); // 사이트 부담·차단 방지
  }

  if (alerts.length) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(),
      `[BUYMA] 재고 확인 필요 ${alerts.length}건`,
      '아래 상품을 확인하세요:\n\n' + alerts.join('\n'));
  }
}

// 매일 오전 9시 자동 실행 트리거 1회만 설정
function setupDailyTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('checkStockDaily').timeBased().everyDays(1).atHour(9).create();
}
```

운영 메일로 받으려면 `Session.getActiveUser().getEmail()`을 `'goyu.studio.help@gmail.com'`으로 바꿔도 됨.

---

## 4. ⚠️ "매일 자동 체크" 가능 범위 (솔직)

| 동작 | 가능? | 비고 |
|---|---|---|
| **오래된 행 알림**(경과 3일↑ 자동 표시·메일) | 🟢 **100% 가능** | T열 + 스크립트 메일. 가장 확실 |
| **품절 자동 감지**(서버렌더 HTML 사이트) | 🟢 가능 | "품절/sold out" 텍스트가 HTML에 있으면 잡음 |
| **품절 감지**(SPA·JS 렌더 사이트) | 🔴 **불가** | UrlFetchApp은 원시 HTML만 → JS로 그리는 재고는 못 읽음. 한국몰 다수가 이 케이스 |
| **로그인·봇차단(Cloudflare) 페이지** | 🔴 불가 | 접근 차단 → '要確認'으로 표시됨 |
| 무신사 등 대형몰 상세 | 🟡 일부 | 구조 바뀌면 깨짐. 키워드 방식이라 오탐 가능 |

**현실 운영법:**
- 자동체크는 **1차 필터**(확실한 품절·접근불가만 거름) + **오래된 행 리마인더**로 쓴다.
- `要確認` 뜬 것만 **사람이 1분 눈으로 확인** → 100% 자동 신뢰 금지.
- 무재고 핵심 리스크 = 주문 후 사입 품절. 그래서 **주문 들어오면 그 자리에서 재확인**이 가장 중요(스크립트는 보조).
- 사이트 부담·차단 방지로 `sleep` 유지, 과도한 빈도(매시간 등) 금지 → **하루 1회**가 적정.

> ⚖️ 스크래핑은 공개 페이지의 비개인정보 범위로만. 사입처 ToS 위반·과도 요청 금지(하루 1회·딜레이 준수).

---

## 5. 권장 운영 사이클
1. 신규 상품 → 시트에 F~I, C·D·E, P 입력 → J~O 자동, **공식 CSV로 일괄출품**(12번)
2. 매일 오전 9시 자동체크 → `要確認`만 손으로 확인
3. 환율(I) 주 1회 갱신 → 판매가 일괄 재계산
4. 주문 발생 → **그 자리서 사입처 재확인** 후 사입·발송(11번 흐름)

*연계: 마진식 11번 · 출품 샘플/공식CSV 12번 · CSV 파일 `product/buyma_inventory_template.csv`*
