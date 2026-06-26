// The Kala Lawyers - Client-Side Admin Dashboard Controller
document.addEventListener("DOMContentLoaded", async function () {
  // Ensure Supabase Client is loaded and configured
  if (!supabaseClient) {
    console.warn("Supabase Client is not configured. Admin functions are disabled.");
    return;
  }

  //--------------------------------------------------------------------------------------------------//
  // 1. Auth Gatekeeper (Login / Session Handling)
  //--------------------------------------------------------------------------------------------------//
  const loginForm = document.getElementById("loginForm");
  
  if (loginForm) {
    // We are on admin_login.html page
    loginForm.addEventListener("submit", handleAdminLogin);
    return;
  }

  // We are on admin.html - verify authentication session
  const { data: { user }, error } = await supabaseClient.auth.getUser();
  if (error || !user) {
    console.log("No active admin session. Redirecting to login page...");
    window.location.href = "admin_login.html";
    return;
  }

  console.log("Authenticated as:", user.email);

  // Bind logout action
  const logoutBtn = document.getElementById("logoutBtn") || document.querySelector("a[href*='logout']");
  if (logoutBtn) {
    logoutBtn.removeAttribute("href");
    logoutBtn.style.cursor = "pointer";
    logoutBtn.addEventListener("click", async function (e) {
      e.preventDefault();
      await supabaseClient.auth.signOut();
      window.location.href = "admin_login.html";
    });
  }

  //--------------------------------------------------------------------------------------------------//
  // 2. Global State Variables & Initialization
  //--------------------------------------------------------------------------------------------------//
  let allLeads = [];
  let allCases = [];
  let allPractices = [];
  let referralChartInstance = null;
  let practiceChartInstance = null;
  
  let searchQuery = "";
  let practiceFilter = "";

  // Bind Search and Filter Inputs
  const leadSearch = document.getElementById("leadSearch");
  if (leadSearch) {
    leadSearch.addEventListener("input", function() {
      searchQuery = this.value.toLowerCase().trim();
      renderLeadsTable();
    });
  }

  const leadFilter = document.getElementById("leadPracticeFilter");
  if (leadFilter) {
    leadFilter.addEventListener("change", function() {
      practiceFilter = this.value;
      renderLeadsTable();
    });
  }

  // Initialize data load
  loadDashboardData();

  //--------------------------------------------------------------------------------------------------//
  // 3. Database Fetch & Load Operations
  //--------------------------------------------------------------------------------------------------//
  async function loadDashboardData() {
    try {
      // Fetch Leads (Enquiries)
      const { data: leadsData, error: leadsErr } = await supabaseClient
        .from('enquiries')
        .select('*')
        .order('timestamp', { ascending: false });
      
      if (leadsErr) throw leadsErr;
      allLeads = leadsData || [];

      // Fetch Case Wins
      const { data: casesData, error: casesErr } = await supabaseClient
        .from('case_wins')
        .select('*')
        .order('date_added', { ascending: false });
        
      if (casesErr) throw casesErr;
      allCases = casesData || [];

      // Fetch Practice Areas
      const { data: practicesData, error: practicesErr } = await supabaseClient
        .from('practice_areas')
        .select('*');
        
      if (practicesErr) throw practicesErr;
      allPractices = practicesData || [];

      // Render tab numbers
      updateTabBadges();

      // Render views & KPI stats
      renderKPIs();
      renderLeadsTable();
      renderCasesGrid();
      renderPracticesGrid();
      
      // Render charts
      renderAnalyticsCharts();

    } catch (err) {
      console.error("Error loading dashboard data:", err);
      alert("Error loading data from Supabase. Make sure the database tables are created.");
    }
  }

  function updateTabBadges() {
    const leadsTabBtn = document.querySelector("button[onclick*='tab-leads']");
    if (leadsTabBtn) leadsTabBtn.textContent = `Client Enquiries (${allLeads.length})`;

    const casesTabBtn = document.querySelector("button[onclick*='tab-cases']");
    if (casesTabBtn) casesTabBtn.textContent = `Successful Case Wins (${allCases.length})`;

    const practicesTabBtn = document.querySelector("button[onclick*='tab-practices']");
    if (practicesTabBtn) practicesTabBtn.textContent = `Practice Areas (${allPractices.length})`;
  }

  function renderKPIs() {
    const totalLeadsEl = document.getElementById("kpiTotalLeads");
    const totalCasesEl = document.getElementById("kpiTotalCases");
    const totalPracticesEl = document.getElementById("kpiTotalPractices");
    const pendingLeadsEl = document.getElementById("kpiPendingLeads");
    
    if (totalLeadsEl) totalLeadsEl.textContent = allLeads.length;
    if (totalCasesEl) totalCasesEl.textContent = allCases.length;
    if (totalPracticesEl) totalPracticesEl.textContent = allPractices.length;
    if (pendingLeadsEl) {
      const pendingCount = allLeads.filter(l => l.status === 'New' || !l.status).length;
      pendingLeadsEl.textContent = pendingCount;
    }
  }

  //--------------------------------------------------------------------------------------------------//
  // 4. Enquiries (Leads) Rendering & Actions
  //--------------------------------------------------------------------------------------------------//
  function renderLeadsTable() {
    const tbody = document.getElementById("leadsTableBody");
    const container = document.getElementById("leadsTableContainer");
    const noLeadsMsg = document.getElementById("noLeadsMessage");
    const exportBtn = document.querySelector(".export-btn");
    
    if (!tbody) return;
    tbody.innerHTML = '';

    // Apply client-side search & filtering
    let filteredLeads = allLeads;
    if (searchQuery) {
      filteredLeads = filteredLeads.filter(lead => 
        (lead.name || "").toLowerCase().includes(searchQuery) ||
        (lead.email || "").toLowerCase().includes(searchQuery) ||
        (lead.phone || "").toLowerCase().includes(searchQuery) ||
        (lead.message || "").toLowerCase().includes(searchQuery)
      );
    }
    if (practiceFilter) {
      filteredLeads = filteredLeads.filter(lead => lead.practice_area === practiceFilter);
    }

    if (filteredLeads.length === 0) {
      if (container) container.style.display = "none";
      if (noLeadsMsg) {
        noLeadsMsg.style.display = "block";
        noLeadsMsg.textContent = searchQuery || practiceFilter ? "No enquiries match your search filters." : "No client evaluations or enquiries have been logged yet.";
      }
      if (exportBtn) exportBtn.style.display = "none";
      return;
    }

    if (container) container.style.display = "block";
    if (noLeadsMsg) noLeadsMsg.style.display = "none";
    if (exportBtn) {
      exportBtn.style.display = "inline-block";
      exportBtn.removeAttribute("href");
      exportBtn.style.cursor = "pointer";
      exportBtn.onclick = (e) => {
        e.preventDefault();
        exportLeadsToCSV(filteredLeads);
      };
    }

    filteredLeads.forEach(lead => {
      const tr = document.createElement("tr");
      
      let dateStr = lead.timestamp || "N/A";
      let timeStr = "";
      if (dateStr.includes("T")) {
        const parts = dateStr.split("T");
        dateStr = parts[0];
        timeStr = parts[1].substring(0, 5);
      }

      // Generate status select options
      const currentStatus = lead.status || 'New';
      let selectClass = "status-new";
      if (currentStatus === 'In Progress') selectClass = "status-progress";
      if (currentStatus === 'Contacted') selectClass = "status-contacted";
      if (currentStatus === 'Resolved') selectClass = "status-resolved";

      // Truncate message for grid preview and show "View Full Message" button
      let messagePreview = escapeHtml(lead.message || '');
      let readMoreHtml = '';
      if (lead.message && lead.message.length > 40) {
        messagePreview = escapeHtml(lead.message.substring(0, 40)) + '...';
        readMoreHtml = `<br/><button type="button" class="btn-view-msg" style="background: none; border: none; color: var(--accent-color); font-weight: 700; cursor: pointer; padding: 4px 0 0 0; font-size: 0.8rem; text-decoration: underline; font-family: inherit;">View Full Message</button>`;
      }

      tr.innerHTML = `
        <td class="timestamp">
          ${dateStr}<br/>
          <small>${timeStr}</small>
        </td>
        <td style="font-weight: 700; color: var(--highlight-color); word-break: break-word;">${escapeHtml(lead.name)}</td>
        <td>
          <strong>Area:</strong> <span style="color: var(--primary-color); font-weight: 600;">${escapeHtml(lead.practice_area || 'General')}</span><br/>
          <small>${escapeHtml(lead.company || 'N/A')}</small>
        </td>
        <td style="word-break: break-all;">
          <strong>Email:</strong> <a href="mailto:${lead.email}" style="color: var(--accent-color); font-weight: 500;">${escapeHtml(lead.email)}</a><br/>
          <strong>Phone:</strong> <a href="tel:${lead.phone}" style="color: var(--accent-color); font-weight: 500;">${escapeHtml(lead.phone)}</a>
        </td>
        <td>${escapeHtml(lead.referred_by || 'Direct')}</td>
        <td style="max-width: 150px; word-wrap: break-word; color: var(--text-color); font-size: 0.9rem; line-height: 1.4;">${messagePreview}${readMoreHtml}</td>
        <td>
          <select class="lead-status-select ${selectClass}" data-id="${lead.id}">
            <option value="New" ${currentStatus === 'New' ? 'selected' : ''}>New</option>
            <option value="In Progress" ${currentStatus === 'In Progress' ? 'selected' : ''}>In Progress</option>
            <option value="Contacted" ${currentStatus === 'Contacted' ? 'selected' : ''}>Contacted</option>
            <option value="Resolved" ${currentStatus === 'Resolved' ? 'selected' : ''}>Resolved</option>
          </select>
        </td>
        <td>
          <button class="btn-delete" style="border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer;">Delete</button>
        </td>
      `;

      // Bind view full message action
      const viewMsgBtn = tr.querySelector(".btn-view-msg");
      if (viewMsgBtn) {
        viewMsgBtn.addEventListener("click", () => {
          openEnquiryModal(lead);
        });
      }

      // Bind status select change
      const statusSelect = tr.querySelector(".lead-status-select");
      statusSelect.addEventListener("change", async function() {
        const leadId = this.getAttribute("data-id");
        const nextStatus = this.value;
        this.disabled = true;
        
        try {
          const { error } = await supabaseClient
            .from('enquiries')
            .update({ status: nextStatus })
            .match({ id: leadId });
            
          if (error) throw error;
          
          // Update status in state quietly
          allLeads = allLeads.map(l => l.id == leadId ? { ...l, status: nextStatus } : l);
          
          // Re-style select class
          this.className = "lead-status-select";
          if (nextStatus === 'New') this.classList.add("status-new");
          if (nextStatus === 'In Progress') this.classList.add("status-progress");
          if (nextStatus === 'Contacted') this.classList.add("status-contacted");
          if (nextStatus === 'Resolved') this.classList.add("status-resolved");
          
          renderKPIs();
        } catch (err) {
          console.error("Failed to update status:", err);
          alert("Error updating status: " + err.message);
          this.value = currentStatus; // revert
        } finally {
          this.disabled = false;
        }
      });

      // Bind delete action
      const deleteBtn = tr.querySelector(".btn-delete");
      deleteBtn.addEventListener("click", async () => {
        if (confirm(`Are you sure you want to delete lead from ${lead.name}?`)) {
          deleteBtn.disabled = true;
          deleteBtn.textContent = "Deleting...";
          const { error } = await supabaseClient.from('enquiries').delete().match({ id: lead.id });
          if (error) {
            alert("Error deleting lead: " + error.message);
            deleteBtn.disabled = false;
            deleteBtn.textContent = "Delete";
          } else {
            loadDashboardData();
          }
        }
      });

      tbody.appendChild(tr);
    });
  }

  function openEnquiryModal(lead) {
    const oldModal = document.querySelector(".enquiry-modal");
    if (oldModal) oldModal.remove();

    const modal = document.createElement("div");
    modal.className = "enquiry-modal";
    modal.style.position = "fixed";
    modal.style.top = "0";
    modal.style.left = "0";
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.backgroundColor = "rgba(45, 34, 28, 0.4)";
    modal.style.backdropFilter = "blur(4px)";
    modal.style.display = "flex";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    modal.style.zIndex = "9999";
    modal.style.opacity = "0";
    modal.style.transition = "opacity 0.2s ease";

    const modalContent = document.createElement("div");
    modalContent.className = "enquiry-modal-content";
    modalContent.style.backgroundColor = "var(--bg-card, #ffffff)";
    modalContent.style.width = "90%";
    modalContent.style.maxWidth = "600px";
    modalContent.style.borderRadius = "12px";
    modalContent.style.boxShadow = "var(--shadow-premium)";
    modalContent.style.borderTop = "6px solid var(--accent-color)";
    modalContent.style.padding = "2.5rem";
    modalContent.style.boxSizing = "border-box";
    modalContent.style.transform = "scale(0.95)";
    modalContent.style.transition = "transform 0.2s ease";

    let dateStr = lead.timestamp || "N/A";
    let timeStr = "";
    if (dateStr.includes("T")) {
      const parts = dateStr.split("T");
      dateStr = parts[0];
      timeStr = parts[1].substring(0, 5);
    }

    modalContent.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h2 style="margin: 0; font-family: 'Merriweather', Georgia, serif; font-size: 1.6rem; color: var(--primary-color); font-weight: normal;">Enquiry Details</h2>
          <p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: var(--light-text); font-family: monospace;">Received: ${dateStr} at ${timeStr}</p>
        </div>
        <button class="enquiry-modal-close" style="background: none; border: none; font-size: 2rem; color: var(--light-text); cursor: pointer; padding: 0; line-height: 1;">&times;</button>
      </div>
      
      <div style="max-height: 380px; overflow-y: auto; padding-right: 8px;">
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.95rem;">
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; font-weight: bold; color: var(--light-text); width: 30%;">Client Name:</td>
            <td style="padding: 0.6rem 0; font-weight: bold; color: var(--primary-color);">${escapeHtml(lead.name)}</td>
          </tr>
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; color: var(--light-text);">Email Address:</td>
            <td style="padding: 0.6rem 0;"><a href="mailto:${lead.email}" style="color: var(--accent-color); text-decoration: none; font-weight: bold;">${escapeHtml(lead.email)}</a></td>
          </tr>
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; color: var(--light-text);">Phone Number:</td>
            <td style="padding: 0.6rem 0;"><a href="tel:${lead.phone}" style="color: var(--accent-color); text-decoration: none; font-weight: bold;">${escapeHtml(lead.phone)}</a></td>
          </tr>
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; color: var(--light-text);">Concern Area:</td>
            <td style="padding: 0.6rem 0; font-weight: bold; color: var(--accent-color);">${escapeHtml(lead.practice_area || 'General')}</td>
          </tr>
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; color: var(--light-text);">Company / Org:</td>
            <td style="padding: 0.6rem 0;">${escapeHtml(lead.company || 'N/A')}</td>
          </tr>
          <tr style="border-bottom: 1px solid #fcfbfa;">
            <td style="padding: 0.6rem 0; color: var(--light-text);">Referred By:</td>
            <td style="padding: 0.6rem 0;">${escapeHtml(lead.referred_by || 'Direct')}</td>
          </tr>
        </table>
        
        <h3 style="font-family: 'Merriweather', Georgia, serif; font-size: 1.1rem; color: var(--primary-color); margin-top: 1.5rem; margin-bottom: 0.8rem; font-weight: normal; border-bottom: 1px solid var(--border-color); padding-bottom: 0.4rem;">Enquiry Message</h3>
        <div style="background-color: #faf8f5; border-left: 3px solid var(--accent-color); padding: 1.2rem; border-radius: 0 6px 6px 0; font-size: 0.95rem; color: #4a3e38; line-height: 1.6; font-style: italic; white-space: pre-wrap; word-break: break-word;">${escapeHtml(lead.message)}</div>
      </div>
      
      <div style="margin-top: 2rem; display: flex; justify-content: flex-end; border-top: 1px solid var(--border-color); padding-top: 1.2rem;">
        <button class="enquiry-modal-btn-close" style="background-color: var(--accent-color); color: #ffffff; border: none; padding: 0.6rem 1.8rem; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background-color 0.2s;">Close View</button>
      </div>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    setTimeout(() => {
      modal.style.opacity = "1";
      modalContent.style.transform = "scale(1)";
    }, 10);

    const closeModal = () => {
      modal.style.opacity = "0";
      modalContent.style.transform = "scale(0.95)";
      setTimeout(() => {
        modal.remove();
      }, 200);
    };

    modalContent.querySelector(".enquiry-modal-close").addEventListener("click", closeModal);
    modalContent.querySelector(".enquiry-modal-btn-close").addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });

    const handleEscape = (e) => {
      if (e.key === "Escape") {
        closeModal();
        document.removeEventListener("keydown", handleEscape);
      }
    };
    document.addEventListener("keydown", handleEscape);
  }

  function exportLeadsToCSV(leadsToExport) {
    const list = leadsToExport || allLeads;
    if (list.length === 0) return;
    let csv = 'ID,Timestamp,Status,Name,Company,Email,Phone,Referred By,Practice Area,Message\n';
    list.forEach(c => {
      const msg = (c.message || '').replace(/"/g, '""');
      const company = (c.company || 'N/A').replace(/"/g, '""');
      const status = c.status || 'New';
      csv += `${c.id},"${c.timestamp}","${status}","${c.name}","${company}","${c.email}","${c.phone}","${c.referred_by}","${c.practice_area}","${msg}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "enquiry_leads.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  //--------------------------------------------------------------------------------------------------//
  // 5. Case Wins CMS Rendering & Forms
  //--------------------------------------------------------------------------------------------------//
  const caseForm = document.getElementById("caseForm");
  if (caseForm) {
    caseForm.removeAttribute("action");
    caseForm.addEventListener("submit", handleCaseFormSubmit);
    
    // Bind reset/cancel edit button
    const caseResetBtn = document.getElementById("caseResetBtn");
    if (caseResetBtn) {
      caseResetBtn.onclick = resetCaseWinForm;
    }
  }

  function renderCasesGrid() {
    const listContainer = document.getElementById("casesListContainer") || document.querySelector(".cms-list");
    if (!listContainer) return;

    // Find or create grid container
    let grid = document.getElementById("casesStaticGrid");
    if (!grid) {
      grid = document.createElement("div");
      grid.id = "casesStaticGrid";
      grid.className = "cms-grid-layout";
      grid.style.display = "grid";
      grid.style.gridTemplateColumns = "repeat(auto-fill, minmax(300px, 1fr))";
      grid.style.gap = "1.5rem";
      grid.style.marginTop = "1rem";
      
      // Clean old static loop elements
      const existingItems = listContainer.querySelectorAll(".cms-item-card");
      existingItems.forEach(item => item.remove());
      
      // Insert grid after header
      const header = listContainer.querySelector("h3");
      if (header) {
        header.after(grid);
      } else {
        listContainer.appendChild(grid);
      }
    }

    grid.innerHTML = '';
    const noCasesMsg = document.getElementById("noCasesMessage");

    if (allCases.length === 0) {
      if (noCasesMsg) noCasesMsg.style.display = "block";
      return;
    }
    if (noCasesMsg) noCasesMsg.style.display = "none";

    allCases.forEach(caseItem => {
      const card = document.createElement("div");
      card.className = "cms-item-card";
      card.id = `case-card-${caseItem.id}`;
      
      let pdfFilenameText = caseItem.pdf_filename || "None";
      
      card.innerHTML = `
        <h4>${escapeHtml(caseItem.title)}</h4>
        <p style="font-size: 0.85rem; color: var(--accent-color); margin-bottom: 0.8rem; font-family: monospace;">
          📄 PDF File: ${escapeHtml(pdfFilenameText)}
        </p>
        <p>${escapeHtml(caseItem.description)}</p>
        <div class="cms-item-actions" style="margin-top: 1rem; display: flex; gap: 0.8rem;">
          <button class="btn-edit" style="border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer;">Edit</button>
          <button class="btn-delete" style="border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; background-color: #ef4444; color: white;">Delete</button>
        </div>
      `;

      // Bind edit action
      card.querySelector(".btn-edit").addEventListener("click", () => {
        editCaseWin(caseItem);
      });

      // Bind delete action
      card.querySelector(".btn-delete").addEventListener("click", async () => {
        if (confirm(`Delete case win: "${caseItem.title}"?`)) {
          const { error } = await supabaseClient.from('case_wins').delete().match({ id: caseItem.id });
          if (error) {
            alert("Error deleting case win: " + error.message);
          } else {
            loadDashboardData();
          }
        }
      });

      grid.appendChild(card);
    });
  }

  function editCaseWin(caseObj) {
    document.getElementById("caseFormTitle").textContent = "Edit Case Win";
    document.getElementById("case_id").value = caseObj.id;
    document.getElementById("case_title").value = caseObj.title;
    document.getElementById("case_category").value = caseObj.category || "";
    document.getElementById("case_pdf").value = caseObj.pdf_filename || "";
    document.getElementById("case_desc").value = caseObj.description;

    document.getElementById("caseResetBtn").style.display = "block";
    document.getElementById("caseFormTitle").scrollIntoView({ behavior: "smooth" });
  }

  function resetCaseWinForm() {
    document.getElementById("caseFormTitle").textContent = "Add Case Win";
    document.getElementById("caseForm").reset();
    document.getElementById("case_id").value = "";
    document.getElementById("caseResetBtn").style.display = "none";
  }

  async function handleCaseFormSubmit(e) {
    e.preventDefault();
    const caseId = document.getElementById("case_id").value;
    const title = document.getElementById("case_title").value;
    const category = document.getElementById("case_category").value;
    const description = document.getElementById("case_desc").value;
    const fileInput = document.getElementById("case_pdf_file");
    let pdfFilename = document.getElementById("case_pdf").value;

    const submitBtn = document.getElementById("caseSubmitBtn");
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "SAVING...";
    submitBtn.disabled = true;

    try {
      // 1. Handle File Upload to Supabase Storage if a new file is selected
      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileExt = file.name.split('.').pop();
        const safeName = `${Math.random().toString(36).substring(2, 15)}_${Date.now()}.${fileExt}`;
        
        const { data, error: uploadErr } = await supabaseClient.storage
          .from('case-judgments')
          .upload(safeName, file);
          
        if (uploadErr) throw uploadErr;
        pdfFilename = safeName;
      }

      // 2. Insert or Update Database row
      const payload = {
        title: title,
        category: category,
        pdf_filename: pdfFilename,
        description: description
      };

      if (caseId) {
        // Edit mode
        const { error: dbErr } = await supabaseClient
          .from('case_wins')
          .update(payload)
          .match({ id: caseId });
          
        if (dbErr) throw dbErr;
      } else {
        // New mode
        payload.date_added = new Date().toISOString();
        const { error: dbErr } = await supabaseClient
          .from('case_wins')
          .insert([payload]);
          
        if (dbErr) throw dbErr;
      }

      resetCaseWinForm();
      loadDashboardData();
      alert("Case Win saved successfully!");

    } catch (err) {
      console.error("Error saving case win:", err);
      alert("Error saving case win: " + err.message);
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  }

  //--------------------------------------------------------------------------------------------------//
  // 6. Practice Areas CMS Rendering & Editing
  //--------------------------------------------------------------------------------------------------//
  const practiceForm = document.getElementById("practiceForm");
  if (practiceForm) {
    practiceForm.removeAttribute("action");
    practiceForm.addEventListener("submit", handlePracticeFormSubmit);
  }

  function renderPracticesGrid() {
    const listContainer = document.querySelector("#tab-practices .cms-list");
    if (!listContainer) return;

    listContainer.innerHTML = '<h3>Available Practice Areas</h3>';

    allPractices.forEach(practice => {
      const card = document.createElement("div");
      card.className = "cms-item-card";
      card.id = `practice-card-${practice.id}`;

      card.innerHTML = `
        <h4 style="color: var(--highlight-color);">${practice.icon || '⚖️'} ${escapeHtml(practice.title)}</h4>
        <p><strong>Short Description:</strong> ${escapeHtml(practice.short_description)}</p>
        <div class="cms-item-actions" style="margin-top: 1rem;">
          <button class="btn-edit" style="border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer;">Edit Details</button>
        </div>
      `;

      card.querySelector(".btn-edit").addEventListener("click", () => {
        loadPracticeAreaForEdit(practice);
      });

      listContainer.appendChild(card);
    });
  }

  window.loadPracticeAreaForEdit = function (practiceObj) {
    document.getElementById("practice_title").value = practiceObj.title;
    document.getElementById("practice_short").value = practiceObj.short_description;
    document.getElementById("practice_long").value = practiceObj.long_description;

    // Parse specialties and statutes back to lines
    let specs = [];
    if (typeof practiceObj.specialties === 'string') {
      try { specs = JSON.parse(practiceObj.specialties); } catch (e) { specs = [practiceObj.specialties]; }
    } else {
      specs = practiceObj.specialties || [];
    }

    let stats = [];
    if (typeof practiceObj.statutes === 'string') {
      try { stats = JSON.parse(practiceObj.statutes); } catch (e) { stats = [practiceObj.statutes]; }
    } else {
      stats = practiceObj.statutes || [];
    }

    document.getElementById("practice_specialties").value = specs.join("\n");
    document.getElementById("practice_statutes").value = stats.join("\n");
    
    // Store practice ID in form data attribute
    practiceForm.setAttribute("data-id", practiceObj.id);

    // Enable submit button
    document.getElementById("practiceSubmitBtn").removeAttribute("disabled");
    document.getElementById("practiceForm").scrollIntoView({ behavior: "smooth" });
  };

  async function handlePracticeFormSubmit(e) {
    e.preventDefault();
    const practiceId = this.getAttribute("data-id");
    const shortDesc = document.getElementById("practice_short").value;
    const longDesc = document.getElementById("practice_long").value;
    const specialtiesText = document.getElementById("practice_specialties").value;
    const statutesText = document.getElementById("practice_statutes").value;

    if (!practiceId) return;

    const submitBtn = document.getElementById("practiceSubmitBtn");
    submitBtn.textContent = "SAVING...";
    submitBtn.disabled = true;

    const specialtiesList = specialtiesText.split('\n').map(s => s.trim()).filter(Boolean);
    const statutesList = statutesText.split('\n').map(s => s.trim()).filter(Boolean);

    try {
      const { error } = await supabaseClient
        .from('practice_areas')
        .update({
          short_description: shortDesc,
          long_description: longDesc,
          specialties: specialtiesList,
          statutes: statutesList
        })
        .match({ id: practiceId });

      if (error) throw error;

      loadDashboardData();
      alert("Practice Area updated in database successfully!\n\nNote: Since this is a static site, you must run build_static.py and redeploy to update public HTML pages for SEO.");
      
      // Reset form
      practiceForm.reset();
      practiceForm.removeAttribute("data-id");
      submitBtn.setAttribute("disabled", "true");

    } catch (err) {
      console.error("Error updating practice area:", err);
      alert("Error updating practice area: " + err.message);
    } finally {
      submitBtn.textContent = "SAVE CHANGES";
      submitBtn.disabled = false;
    }
  }

  //--------------------------------------------------------------------------------------------------//
  // 7. Live Analytics Charts rendering
  //--------------------------------------------------------------------------------------------------//
  function renderAnalyticsCharts() {
    // 1. Group leads by referral source
    const referralStats = {};
    const practiceStats = {};

    allLeads.forEach(lead => {
      const ref = lead.referred_by || 'Direct';
      referralStats[ref] = (referralStats[ref] || 0) + 1;

      const area = lead.practice_area || 'General Inquiry';
      practiceStats[area] = (practiceStats[area] || 0) + 1;
    });

    // Destroy old chart instances if they exist (prevents overlapping rendering)
    if (referralChartInstance) referralChartInstance.destroy();
    if (practiceChartInstance) practiceChartInstance.destroy();

    // Render Referral Doughnut Chart
    const refCtx = document.getElementById('referralChart');
    if (refCtx) {
      referralChartInstance = new Chart(refCtx.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(referralStats).length ? Object.keys(referralStats) : ["No data"],
          datasets: [{
            data: Object.values(referralStats).length ? Object.values(referralStats) : [1],
            backgroundColor: Object.keys(referralStats).length ? ['#b38a66', '#a8978e', '#d9b873', '#6b5a50', '#c5a85c', '#5a4b41'] : ['#2d221c'],
            borderColor: '#ffffff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { color: '#6b5a50', font: { family: 'Inter' } }
            }
          }
        }
      });
    }

    // Render Practice Area Bar Chart
    const pracCtx = document.getElementById('practiceChart');
    if (pracCtx) {
      const labels = Object.keys(practiceStats).map(label => {
        return label.length > 20 ? label.substring(0, 17) + '...' : label;
      });

      practiceChartInstance = new Chart(pracCtx.getContext('2d'), {
        type: 'bar',
        data: {
          labels: labels.length ? labels : ["No data"],
          datasets: [{
            label: 'Lead Enquiries',
            data: Object.values(practiceStats).length ? Object.values(practiceStats) : [0],
            backgroundColor: '#b38a66',
            borderColor: '#e5c1a0',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#6b5a50' } },
            y: { grid: { color: 'rgba(45, 34, 28, 0.08)' }, ticks: { color: '#6b5a50', stepSize: 1 } }
          }
        }
      });
    }
  }

  //--------------------------------------------------------------------------------------------------//
  // 8. Admin Login handler
  //--------------------------------------------------------------------------------------------------//
  async function handleAdminLogin(e) {
    e.preventDefault();
    const usernameVal = document.getElementById("username").value;
    const passwordVal = document.getElementById("password").value;
    const submitBtn = this.querySelector('button[type="submit"]');

    submitBtn.textContent = "LOGGING IN...";
    submitBtn.disabled = true;

    // Remove old errors
    const oldErr = document.querySelector(".error-alert");
    if (oldErr) oldErr.remove();

    // Map username to dummy email if no @ is present (Supabase Auth email requirement)
    let email = usernameVal;
    if (!usernameVal.includes("@")) {
      email = `${usernameVal}@kalalawyers.com`;
    }

    try {
      const { data, error } = await supabaseClient.auth.signInWithPassword({
        email: email,
        password: passwordVal
      });

      if (error) throw error;

      console.log("Logged in successfully!");
      window.location.href = "admin.html";

    } catch (err) {
      console.error("Login failed:", err);
      const alertDiv = document.createElement("div");
      alertDiv.className = "error-alert";
      alertDiv.textContent = err.message || "Invalid credentials. Please try again.";
      this.insertBefore(alertDiv, this.firstChild);
      
      submitBtn.textContent = "LOG IN";
      submitBtn.disabled = false;
    }
  }

  // Utility to escape HTML code strings
  function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
