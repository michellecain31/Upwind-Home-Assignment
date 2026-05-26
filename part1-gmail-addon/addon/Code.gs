// Gmail Add-on script: Extracts message parameters, evaluates risks via backend backend, and renders verdict UI.

const BACKEND_URL = "https://bulge-nearby-series.ngrok-free.dev";

const LOGO_URL = "https://cdn-icons-png.flaticon.com/512/8654/8654266.png"; 
const IMAGE_SAFE = "https://cdn-icons-png.flaticon.com/512/4436/4436481.png"; 
const IMAGE_SUSPICIOUS = "https://cdn-icons-png.flaticon.com/512/564/564619.png"; 
const IMAGE_MALICIOUS = "https://cdn-icons-png.flaticon.com/512/752/752755.png"; 

function onGmailMessage(e) {
  const accessor = e.gmail;
  const messageId = accessor.messageId;
  const token = accessor.accessToken;

  // Contextual access scope elevation for the target message
  GmailApp.setCurrentMessageAccessToken(token);
  const message = GmailApp.getMessageById(messageId);

  // Core metadata extraction
  const subject = message.getSubject();
  const sender = message.getFrom();
  const body = message.getPlainBody(); // Limitation: Plain text bypasses HTML-embedded vectors
  const replyTo = message.getReplyTo();

  const urls = extractUrls(body);

  const payload = {
    subject: subject,
    sender: sender,
    reply_to: replyTo,
    body: body,
    urls: urls
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true, // Prevents Apps Script crash on non-200 responses
    headers: {
      "ngrok-skip-browser-warning": "true" // Required utility header for ngrok tunnels
    }
  };

  // Synchronous network fetch execution
  const response = UrlFetchApp.fetch(BACKEND_URL + "/scan", options);
  const result = JSON.parse(response.getContentText());

  return buildCard(result, subject, sender);
}

/**
 * Regex-based URL extraction utility.
 * Limitation: Does not handle advanced obfuscation or unicode domain spoofing.
 */
function extractUrls(text) {
  const urlRegex = /https?:\/\/[^\s]+/g;
  return text.match(urlRegex) || [];
}

/**
 * Dynamic UI builder mapping backend scoring to an explainable security card layout.
 */
function buildCard(result, subject, sender) {
  const card = CardService.newCardBuilder();
  
  const cardHeader = CardService.newCardHeader()
    .setTitle("Upwind Michelle Cain")
    .setSubtitle("Email Security Engine")
    .setImageUrl(LOGO_URL)
    .setImageStyle(CardService.ImageStyle.CIRCLE);
  
  card.setHeader(cardHeader);

  const headerSection = CardService.newCardSection();
  
  let verdictColor = "#28a745"; 
  let verdictIcon = "✅";
  let statusImage = IMAGE_SAFE; 
  
  if (result.verdict === "MALICIOUS") {
    verdictColor = "#dc3545"; 
    verdictIcon = "🚨";
    statusImage = IMAGE_MALICIOUS; 
  } else if (result.verdict === "SUSPICIOUS") {
    verdictColor = "#fd7e14"; 
    verdictIcon = "⚠️";
    statusImage = IMAGE_SUSPICIOUS; 
  }

  // Renders aggregate threat categorization and raw score
  headerSection.addWidget(
    CardService.newDecoratedText()
      .setText(`<font size="large"><b>${verdictIcon} ${result.verdict}</b></font>`)
      .setTopLabel("SECURITY VERDICT")
      .setBottomLabel(`Threat Score: ${result.total_score} / 100`)
      .setStartIcon(CardService.newIconImage().setIconUrl(statusImage))
  );

  headerSection.addWidget(
    CardService.newTextParagraph().setText(
      `<b>From:</b> ${sender}`
    )
  );
  
  headerSection.addWidget(CardService.newDivider());
  card.addSection(headerSection);

  const signalsSection = CardService.newCardSection().setHeader("Signal Breakdown");

  // Dynamic mapping decouples UI presentation from backend calculation rules
  result.signals.forEach(signal => {
    if (signal.score > 0) {
      signalsSection.addWidget(
        CardService.newTextParagraph().setText(
          `🔸 <b><font color="#dc3545">${signal.name}</font></b> <font color="#dc3545">(+${signal.score} pts)</font><br>` +
          `<font color="#555555"><i>${signal.detail}</i></font>`
        )
      );
    } else {
      signalsSection.addWidget(
        CardService.newTextParagraph().setText(
          `🔹 <b><font color="#28a745">${signal.name}</font></b> (0 pts)<br>` +
          `<font color="#888888"><i>${signal.detail}</i></font>`
        )
      );
    }
  });

  card.addSection(signalsSection);

  const footerSection = CardService.newCardSection();
  footerSection.addWidget(CardService.newDivider());
  
  // Interactive navigation to state history view
  const historyButton = CardService.newTextButton()
    .setText("📜 View Recent Scans")
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
    .setOnClickAction(CardService.newAction().setFunctionName("getHistory"));
    
  footerSection.addWidget(CardService.newButtonSet().addButton(historyButton));
  card.addSection(footerSection);

  return card.build();
}

/**
 * History view retrieval using standard CardService callback.
 */
function getHistory(e) {
  const options = {
    method: "get",
    muteHttpExceptions: true,
    headers: {
      "ngrok-skip-browser-warning": "true"
    }
  };

  const response = UrlFetchApp.fetch(BACKEND_URL + "/history", options);
  const scans = JSON.parse(response.getContentText());

  const card = CardService.newCardBuilder();
  const section = CardService.newCardSection().setHeader("Recent Scans History");

  // UX Optimization: Constrains layout bounds to the top 10 historical entries
  scans.slice(0, 10).forEach(scan => {
    let verdictColor = "#28a745"; 
    if (scan.verdict === "MALICIOUS") verdictColor = "#dc3545";
    else if (scan.verdict === "SUSPICIOUS") verdictColor = "#fd7e14";

    section.addWidget(
      CardService.newTextParagraph().setText(
        `<b><font color="${verdictColor}">${scan.verdict}</font></b> <code>(${scan.total_score}/100)</code><br>` +
        `<b>Sender:</b> ${scan.sender}<br>` +
        `<font color="#888888" size="small">Time: ${scan.scanned_at}</font>`
      )
    ).addWidget(CardService.newDivider());
  });

  card.addSection(section);
  return card.build();
}