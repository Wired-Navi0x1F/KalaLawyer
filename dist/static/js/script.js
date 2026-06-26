// The Kala Lawyers - Core Interactive Script
document.addEventListener("DOMContentLoaded", function () {
  const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);
  
  //--------------------------------------------------------------------------------------------------//
  // 0. Manual Image Carousel Slider
  //--------------------------------------------------------------------------------------------------//
  const slider = document.querySelector(".slider");
  const slides = document.querySelectorAll(".slider img");
  const leftArrow = document.querySelector(".left-arrow");
  const rightArrow = document.querySelector(".right-arrow");
  
  let currentIndex = 0;
  
  function goToSlide(index) {
    if (!slides || slides.length === 0) return;
    if (index < 0) {
      currentIndex = slides.length - 1;
    } else if (index >= slides.length) {
      currentIndex = 0;
    } else {
      currentIndex = index;
    }
    const slideWidth = slides[0].clientWidth;
    if (slider) {
      slider.scrollLeft = currentIndex * slideWidth;
    }
  }
  
  if (leftArrow) {
    leftArrow.addEventListener("click", () => {
      goToSlide(currentIndex - 1);
    });
  }
  if (rightArrow) {
    rightArrow.addEventListener("click", () => {
      goToSlide(currentIndex + 1);
    });
  }
  
  document.querySelectorAll(".slider-nav a").forEach((dot, index) => {
    dot.addEventListener("click", (e) => {
      e.preventDefault();
      goToSlide(index);
    });
  });

  //--------------------------------------------------------------------------------------------------//
  // 1. Mobile Burger Menu Toggle
  //--------------------------------------------------------------------------------------------------//
  const burgerMenu = document.getElementById("burgerMenu");
  const navPanel = document.getElementById("navPanel");
  
  if (burgerMenu && navPanel) {
    burgerMenu.addEventListener("click", function (e) {
      e.stopPropagation();
      burgerMenu.classList.toggle("active");
      navPanel.classList.toggle("mobile-active");
    });
    
    // Close menu when clicking outside
    document.addEventListener("click", function (e) {
      if (!navPanel.contains(e.target) && !burgerMenu.contains(e.target)) {
        burgerMenu.classList.remove("active");
        navPanel.classList.remove("mobile-active");
      }
    });

    // Close menu when clicking navigation links
    navPanel.querySelectorAll("a").forEach(link => {
      link.addEventListener("click", () => {
        burgerMenu.classList.remove("active");
        navPanel.classList.remove("mobile-active");
      });
    });
  }

  //--------------------------------------------------------------------------------------------------//
  // 1b. copyPhoneNumber & showToast Systems
  //--------------------------------------------------------------------------------------------------//
  window.copyPhoneNumber = function() {
    const phoneNumber = "+919828117145";
    navigator.clipboard.writeText(phoneNumber).then(() => {
      showToast("📞 Phone number +91 98281 17145 copied to clipboard!");
    }).catch(err => {
      console.error("Failed to copy phone number: ", err);
      // Fallback
      window.location.href = "tel:+919828117145";
    });
  };

  function showToast(message) {
    let toast = document.querySelector(".toast-notification");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "toast-notification";
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<span>${message}</span>`;
    toast.classList.add("show");
    
    setTimeout(() => {
      toast.classList.remove("show");
    }, 3500);
  }

  //--------------------------------------------------------------------------------------------------//
  // 2. 3D Tilt Card Effects
  //--------------------------------------------------------------------------------------------------//
  const tiltCards = document.querySelectorAll(".service-card, .case-card, .contact-person-card, .stat-card");
  if (!isTouchDevice) {
    tiltCards.forEach(card => {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        // Calculate rotation degree (max 8 degrees tilt)
        const rotateX = ((centerY - y) / centerY) * 8;
        const rotateY = ((x - centerX) / centerX) * 8;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
      });
      
      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)";
      });
    });
  }

  //--------------------------------------------------------------------------------------------------//
  // 3. Navigation Hover Preloading
  //--------------------------------------------------------------------------------------------------//
  function preloadPage(url) {
    if (!url || url.includes('#') || url.startsWith('javascript:')) return;
    if (document.querySelector(`link[href="${url}"]`)) return;
    const link = document.createElement("link");
    link.rel = "prefetch";
    link.href = url;
    document.head.appendChild(link);
  }

  document.querySelectorAll("nav a, .nav-panel a").forEach((link) => {
    link.addEventListener("mouseenter", function () {
      const url = this.getAttribute("href");
      preloadPage(url);
    });
  });

  //--------------------------------------------------------------------------------------------------//
  // 4. Contact Form Validation (Red error until correct, then hidden)
  //--------------------------------------------------------------------------------------------------//
  const emailInput = document.getElementById("email");
  const phoneInput = document.getElementById("phone");
  const emailFeedback = document.getElementById("emailFeedback");
  const phoneFeedback = document.getElementById("phoneFeedback");
  
  // Phone regex check (clean space, hyphens, check for +91/0 and 10 digits starting with 6-9)
  function validatePhoneNumber(phoneVal) {
    const cleanPhone = phoneVal.replace(/[\s\-()]/g, '');
    const phoneRegex = /^(?:\+91|0)?([6-9]\d{9})$/;
    const match = cleanPhone.match(phoneRegex);
    return match ? match[1] : null;
  }
  
  if (phoneInput && phoneFeedback) {
    phoneInput.addEventListener("input", function() {
      const cleanNum = validatePhoneNumber(this.value);
      if (this.value.trim() === "") {
        phoneFeedback.style.display = "none";
        phoneInput.style.borderColor = "";
      } else if (cleanNum) {
        phoneFeedback.style.display = "none";
        phoneInput.style.borderColor = "";
      } else {
        phoneFeedback.style.display = "block";
        phoneFeedback.style.color = "#ef4444";
        phoneFeedback.textContent = "✗ Please enter a valid 10-digit Indian phone number.";
        phoneInput.style.borderColor = "#ef4444";
      }
    });
  }
  
  if (emailInput && emailFeedback) {
    emailInput.addEventListener("input", function() {
      const emailVal = this.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (emailVal === "") {
        emailFeedback.style.display = "none";
        emailInput.style.borderColor = "";
      } else if (emailRegex.test(emailVal)) {
        emailFeedback.style.display = "none";
        emailInput.style.borderColor = "";
      } else {
        emailFeedback.style.display = "block";
        emailFeedback.style.color = "#ef4444";
        emailFeedback.textContent = "✗ Please enter a valid email address.";
        emailInput.style.borderColor = "#ef4444";
      }
    });
  }

  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      
      const email = document.getElementById("email").value;
      const phone = document.getElementById("phone").value;
      
      const cleanPhone = validatePhoneNumber(phone);
      if (!cleanPhone) {
        alert("Please enter a valid 10-digit phone number.");
        phoneInput.style.borderColor = "#ef4444";
        if (phoneFeedback) {
          phoneFeedback.style.display = "block";
          phoneFeedback.style.color = "#ef4444";
          phoneFeedback.textContent = "✗ Please enter a valid 10-digit Indian phone number.";
        }
        return;
      } else {
        phoneInput.style.borderColor = "";
        if (phoneFeedback) phoneFeedback.style.display = "none";
      }
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        alert("Please enter a valid email address.");
        emailInput.style.borderColor = "#ef4444";
        if (emailFeedback) {
          emailFeedback.style.display = "block";
          emailFeedback.style.color = "#ef4444";
          emailFeedback.textContent = "✗ Please enter a valid email address.";
        }
        return;
      } else {
        emailInput.style.borderColor = "";
        if (emailFeedback) emailFeedback.style.display = "none";
      }
      
      const submitBtn = document.getElementById("submitBtn");
      const originalText = submitBtn.textContent;
      submitBtn.textContent = "SENDING...";
      submitBtn.disabled = true;
      
      const name = document.getElementById("name").value;
      const company = document.getElementById("company").value;
      const referred_by = document.getElementById("referred_by").value;
      const practice_area = document.getElementById("practice_area").value;
      const message = document.getElementById("message").value;
      
      const cleanPhoneFormatted = "+91" + cleanPhone;
      
      const logData = {
        name: name,
        company: company || "N/A",
        email: email,
        phone: cleanPhoneFormatted,
        referred_by: referred_by,
        practice_area: practice_area,
        message: message,
        timestamp: new Date().toISOString()
      };

      let dbPromise = Promise.resolve();

      if (supabaseClient) {
        dbPromise = supabaseClient
          .from('enquiries')
          .insert([logData])
          .then(({ error }) => {
            if (error) {
              console.warn("Supabase logging returned error: ", error);
            }
          });
      } else {
        dbPromise = fetch("/contact", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify(logData)
        })
        .then(response => {
          if (!response.ok) {
            console.warn("SQLite database logging returned status: " + response.status);
          }
        });
      }

      dbPromise.then(() => {
        const advocateHtml = `
          <h3 style="font-family: Georgia, serif; font-size: 16px; color: #2d221c; margin-top: 30px; margin-bottom: 15px; border-top: 1px solid #f2ebe4; padding-top: 20px; font-weight: normal; text-align: center; text-transform: uppercase; letter-spacing: 1px;">Contact Details</h3>
          <div style="margin-bottom: 15px;">
            <div style="background-color: #fdfbf9; border: 1px solid #f2ebe4; border-radius: 6px; padding: 15px; margin-bottom: 12px;">
              <h4 style="margin: 0; font-family: Georgia, serif; font-size: 14.5px; color: #b38a66; font-weight: normal;">Dr. Shailendra Kala</h4>
              <p style="margin: 2px 0 8px 0; font-size: 10.5px; color: #8c766b; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Senior Advocate</p>
              <table style="border-collapse: collapse; font-size: 13px; color: #5a4b41; width: 100%;">
                <tr>
                  <td style="width: 25px; padding: 3px 0; vertical-align: top; color: #b38a66; font-weight: bold;">📞</td>
                  <td style="padding: 3px 0;"><a href="tel:+919828031187" style="color: #5a4b41; text-decoration: none; font-weight: bold;">+91 98280 31187</a></td>
                </tr>
                <tr>
                  <td style="width: 25px; padding: 3px 0; vertical-align: top; color: #b38a66; font-weight: bold;">✉️</td>
                  <td style="padding: 3px 0;"><a href="mailto:shailendrakala18@gmail.com" style="color: #b38a66; text-decoration: none; font-weight: bold;">shailendrakala18@gmail.com</a></td>
                </tr>
              </table>
            </div>
            
            <div style="background-color: #fdfbf9; border: 1px solid #f2ebe4; border-radius: 6px; padding: 15px;">
              <h4 style="margin: 0; font-family: Georgia, serif; font-size: 14.5px; color: #b38a66; font-weight: normal;">Advocate Anuj Kala</h4>
              <p style="margin: 2px 0 8px 0; font-size: 10.5px; color: #8c766b; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Advocate</p>
              <table style="border-collapse: collapse; font-size: 13px; color: #5a4b41; width: 100%;">
                <tr>
                  <td style="width: 25px; padding: 3px 0; vertical-align: top; color: #b38a66; font-weight: bold;">📞</td>
                  <td style="padding: 3px 0;"><a href="tel:+919828117145" style="color: #5a4b41; text-decoration: none; font-weight: bold;">+91 98281 17145</a></td>
                </tr>
                <tr>
                  <td style="width: 25px; padding: 3px 0; vertical-align: top; color: #b38a66; font-weight: bold;">✉️</td>
                  <td style="padding: 3px 0;"><a href="mailto:advocateanujkalajodhpur@gmail.com" style="color: #b38a66; text-decoration: none; font-weight: bold;">advocateanujkalajodhpur@gmail.com</a></td>
                </tr>
              </table>
            </div>
          </div>
        `;

        // 1. Send lead details to advocates
        return emailjs.send("service_jqmhyjd", "template_i6xtrwj", {
          to_email: "advocateanujkalajodhpur@gmail.com, kalalawyer@gmail.com",
          subject: `New Case Enquiry: ${name} (${practice_area})`,
          email_title: "New Client Enquiry Gateway",
          email_intro: "A new client enquiry has been submitted through the website.",
          name: name,
          company: company || "N/A",
          email: email,
          phone: cleanPhoneFormatted,
          referred_by: referred_by || "Direct",
          practice_area: practice_area,
          message: message,
          advocate_details_section: ""
        })
        .then((adminRes) => {
          console.log("Admin notification email sent successfully:", adminRes.status);
          
          // 2. Send confirmation receipt copy to the client sequentially
          return emailjs.send("service_jqmhyjd", "template_i6xtrwj", {
            to_email: email,
            subject: "Enquiry Received - The Kala Lawyers",
            email_title: "Enquiry Confirmation",
            email_intro: `Dear ${name}, thank you for reaching out to The Kala Lawyers. We have successfully received your case evaluation request. Our legal team will review your details and get back to you shortly to schedule an initial consultation.`,
            name: name,
            company: company || "N/A",
            email: email,
            phone: cleanPhoneFormatted,
            referred_by: referred_by || "Direct",
            practice_area: practice_area,
            message: message,
            advocate_details_section: advocateHtml
          });
        });
      })
      .then((clientRes) => {
        console.log("Client receipt email sent successfully:", clientRes.status);
        document.getElementById("contactFormWrapper").style.display = "none";
        document.getElementById("formSuccess").style.display = "block";
        document.getElementById("formSuccess").scrollIntoView({ behavior: "smooth" });
      })
      .catch((error) => {
        console.error("Submission error details:", error);
        document.getElementById("contactFormWrapper").style.display = "none";
        document.getElementById("formSuccess").style.display = "block";
      })
      .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
      });
    });
  }

  //--------------------------------------------------------------------------------------------------//
  // 5. Successful Case Wins Pagination & PDF modal viewer
  //--------------------------------------------------------------------------------------------------//
  if (document.getElementById("caseGrid")) {
    updateCaseDisplay();
  }

  document.querySelectorAll(".open-pdf-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const pdfUrl = this.getAttribute("href");
      const card = this.closest(".case-card");
      const title = card ? card.querySelector(".case-title").textContent : "Case Judgment";
      openPdfModal(pdfUrl, title);
    });
  });

  // Secret Admin Portal Shortcut (Double-click footer trigger / double-click footer logo / Ctrl+Shift+A)
  function redirectToAdmin() {
    let redirectUrl = "admin.html";
    if (window.location.pathname.includes('/practice/')) {
      redirectUrl = "../admin.html";
    }
    window.location.href = redirectUrl;
  }

  const adminTrigger = document.getElementById("adminTrigger");
  if (adminTrigger) {
    adminTrigger.addEventListener("dblclick", function () {
      redirectToAdmin();
    });
  }

  const footerLogo = document.querySelector(".footer-logo");
  if (footerLogo) {
    footerLogo.addEventListener("dblclick", function () {
      redirectToAdmin();
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'a') {
      redirectToAdmin();
    }
  });

  //--------------------------------------------------------------------------------------------------//
  // 7. Dynamic Supabase Runtime Data Loading (Fallback to pre-rendered static HTML if not configured)
  //--------------------------------------------------------------------------------------------------//
  if (supabaseClient) {
    loadFeaturedCasesFromSupabase();
    loadCasesFromSupabase();
  }

  async function loadFeaturedCasesFromSupabase() {
    const homeGrid = document.querySelector(".cases-home-grid");
    if (!homeGrid) return;
    
    try {
      const { data: cases, error } = await supabaseClient
        .from('case_wins')
        .select('*')
        .order('date_added', { ascending: false })
        .limit(3);
        
      if (error) throw error;
      
      if (cases && cases.length > 0) {
        homeGrid.innerHTML = '';
        cases.forEach(caseWin => {
          const card = document.createElement('div');
          card.className = 'case-home-card';
          
          let linkUrl = "case.html";
          if (window.location.pathname.includes('/practice/')) {
            linkUrl = "../case.html";
          }
          
          card.innerHTML = `
            <h3 class="case-home-title">${caseWin.title}</h3>
            <p class="case-home-desc">${caseWin.description}</p>
            <a href="${linkUrl}" class="case-home-link">
              View Judgments List &rarr;
            </a>
          `;
          homeGrid.appendChild(card);
        });
      }
    } catch (err) {
      console.error("Error loading featured cases from Supabase:", err);
    }
  }

  async function loadCasesFromSupabase() {
    const caseGrid = document.getElementById("caseGrid");
    if (!caseGrid) return;
    
    try {
      const { data: cases, error } = await supabaseClient
        .from('case_wins')
        .select('*')
        .order('date_added', { ascending: false });
        
      if (error) throw error;
      
      if (cases && cases.length > 0) {
        caseGrid.innerHTML = '';
        cases.forEach(pdf => {
          const card = document.createElement('div');
          card.className = 'case-card';
          card.setAttribute('data-title', pdf.title.toLowerCase());
          card.setAttribute('data-description', pdf.description.toLowerCase());
          
          let pdfPath = `static/pdfs/${pdf.pdf_filename}`;
          if (pdf.pdf_filename && (pdf.pdf_filename.startsWith('http://') || pdf.pdf_filename.startsWith('https://'))) {
            pdfPath = pdf.pdf_filename;
          }
          
          let actionsHtml = '';
          if (pdf.pdf_filename) {
            actionsHtml = `
              <a href="${pdfPath}" class="btn open-pdf-btn" data-filename="${pdf.pdf_filename}" target="_blank">View Judgment</a>
              <a href="${pdfPath}" class="btn download" download>Download PDF</a>
            `;
          } else {
            actionsHtml = `
              <span style="font-size: 0.9rem; color: var(--light-text); font-style: italic; font-weight: 500;">
                ⚖️ Document Pending Release
              </span>
            `;
          }
          
          card.innerHTML = `
            <h3 class="case-title">${pdf.title}</h3>
            <p class="case-description">${pdf.description}</p>
            <div class="case-actions">
              ${actionsHtml}
            </div>
          `;
          caseGrid.appendChild(card);
        });
        
        caseGrid.querySelectorAll(".open-pdf-btn").forEach(btn => {
          btn.addEventListener("click", function (e) {
            e.preventDefault();
            const pdfUrl = this.getAttribute("href");
            const title = this.closest(".case-card").querySelector(".case-title").textContent;
            openPdfModal(pdfUrl, title);
          });
        });
        
        currentPage = 1;
        updateCaseDisplay();
      }
    } catch (err) {
      console.error("Error loading case wins from Supabase:", err);
    }
  }
});

// Helper: Open custom PDF Modal
function openPdfModal(pdfLink, title) {
  const oldModal = document.querySelector(".custom-pdf-modal");
  if (oldModal) oldModal.remove();

  const modal = document.createElement("div");
  modal.className = "custom-pdf-modal";
  
  const modalContent = document.createElement("div");
  modalContent.className = "custom-pdf-modal-content";
  
  const modalHeader = document.createElement("div");
  modalHeader.className = "custom-pdf-modal-header";
  
  const h3 = document.createElement("h3");
  h3.textContent = title || "Case Document";
  
  // Container for links/close buttons in the modal header
  const headerActions = document.createElement("div");
  headerActions.style.display = "flex";
  headerActions.style.alignItems = "center";
  headerActions.style.gap = "1.5rem";

  const externalLink = document.createElement("a");
  externalLink.href = pdfLink;
  externalLink.target = "_blank";
  externalLink.textContent = "Open in New Tab ↗";
  externalLink.style.color = "var(--accent-color)";
  externalLink.style.textDecoration = "none";
  externalLink.style.fontWeight = "700";
  externalLink.style.fontSize = "0.9rem";
  externalLink.style.transition = "color 0.2s";
  externalLink.addEventListener("mouseenter", () => externalLink.style.color = "var(--accent-hover)");
  externalLink.addEventListener("mouseleave", () => externalLink.style.color = "var(--accent-color)");

  const closeBtn = document.createElement("button");
  closeBtn.className = "custom-pdf-modal-close";
  closeBtn.innerHTML = "&times;";
  closeBtn.addEventListener("click", () => {
    modal.classList.remove("open");
    modal.style.display = "none";
    modal.remove();
  });

  headerActions.appendChild(externalLink);
  headerActions.appendChild(closeBtn);
  
  const iframeContainer = document.createElement("div");
  iframeContainer.className = "custom-pdf-modal-body";
  
  const iframe = document.createElement("iframe");
  iframe.src = pdfLink;
  iframe.title = title || "PDF document";
  
  modalHeader.appendChild(h3);
  modalHeader.appendChild(headerActions);
  iframeContainer.appendChild(iframe);
  modalContent.appendChild(modalHeader);
  modalContent.appendChild(iframeContainer);
  modal.appendChild(modalContent);
  
  document.body.appendChild(modal);
  
  modal.style.display = "flex";
  modal.classList.add("open");
  
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.remove("open");
      modal.style.display = "none";
      modal.remove();
    }
  });
}

// Case List Pagination (6 items per page)
let currentPage = 1;
const itemsPerPage = 6;

function updateCaseDisplay() {
  const cards = Array.from(document.querySelectorAll(".case-grid .case-card"));
  const totalPages = Math.ceil(cards.length / itemsPerPage);
  
  if (currentPage > totalPages) currentPage = totalPages || 1;
  if (currentPage < 1) currentPage = 1;
  
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  
  cards.forEach((card, index) => {
    if (index >= startIndex && index < endIndex) {
      card.style.display = "flex";
      card.style.opacity = "1";
    } else {
      card.style.display = "none";
    }
  });
  
  const prevBtn = document.getElementById("prevPage");
  const nextBtn = document.getElementById("nextPage");
  const pageInfo = document.getElementById("pageInfo");
  const pagControls = document.getElementById("paginationControls");
  const noResults = document.getElementById("noResults");
  
  if (pagControls) {
    pagControls.style.display = cards.length === 0 ? "none" : "flex";
  }
  
  if (noResults) {
    noResults.style.display = cards.length === 0 ? "block" : "none";
  }
  
  if (prevBtn) prevBtn.disabled = (currentPage === 1);
  if (nextBtn) nextBtn.disabled = (currentPage === totalPages || totalPages === 0);
  if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
}

function changePage(direction) {
  currentPage += direction;
  updateCaseDisplay();
  
  const caseHeader = document.querySelector(".case-page-title");
  if (caseHeader) {
    caseHeader.scrollIntoView({ behavior: "smooth" });
  }
}

//--------------------------------------------------------------------------------------------------//
// 6. Dynamic Location Switcher for Contact Page (KRIA Law style)
//--------------------------------------------------------------------------------------------------//
function switchLocation(target) {
  const btnChamber = document.getElementById("btnChamber");
  const btnResidence = document.getElementById("btnResidence");
  
  const locationType = document.getElementById("locationType");
  const locationAddress = document.getElementById("locationAddress");
  const locationHours = document.getElementById("locationHours");
  const gmapIframe = document.getElementById("gmapIframe");
  
  if (!btnChamber || !btnResidence || !locationType || !locationAddress || !locationHours || !gmapIframe) {
    return;
  }
  
  if (target === 'chamber') {
    btnChamber.classList.add("active");
    btnResidence.classList.remove("active");
    
    locationType.textContent = "Chamber Address";
    locationAddress.innerHTML = "Chamber No. 5, Jubilee Chamber,<br />Heritage Building, Old High Court, Paota,<br />Jodhpur, Rajasthan 342006, India";
    locationHours.innerHTML = "<strong>Monday to Saturday:</strong> 10:00 AM - 5:00 PM (Court Hours)";
    gmapIframe.src = "https://maps.google.com/maps?q=Chamber+No.+5,+Jubilee+Chamber,+Heritage+Building,+Old+High+Court,+Paota,+Jodhpur,+Rajasthan+342006,+India&t=&z=16&ie=UTF8&iwloc=&output=embed";
  } else if (target === 'residence') {
    btnResidence.classList.add("active");
    btnChamber.classList.remove("active");
    
    locationType.textContent = "Office / Residence Address";
    locationAddress.innerHTML = "GIRAH SHOBHA, Advocate Anuj Kala,<br />3-A, Chopasani Rd, Near Nasrani Cinema,<br />Jodhpur, Rajasthan 342003";
    locationHours.innerHTML = "<strong>Monday to Saturday:</strong> 7:00 PM - 11:00 PM<br /><strong>Sunday:</strong> 10:00 AM - 2:00 PM & 7:00 PM - 10:00 PM";
    gmapIframe.src = "https://maps.google.com/maps?q=GIRAH+SHOBHA,+Advocate+Anuj+Kala,+3-A,+Chopasani+Rd,+Near+Nasrani+Cinema,+Jodhpur,+Rajasthan+342003&t=&z=16&ie=UTF8&iwloc=&output=embed";
  }
}
