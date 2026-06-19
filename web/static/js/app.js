function renderAdvancedChart(canvasId, payload) {
    if (!payload || !payload.data) return;

    const styleMeta = payload.chart_style_meta;
    const ctx = document.getElementById(canvasId).getContext('2d');
    const baseType = payload.type;

    let options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: true, position: 'bottom', labels: { boxWidth:12, padding:12, font: { size: 11 }}},
            datalabels: {
                display: true,
                align: function(context) {
                    return ['pie', 'doughnut'].includes(baseType) ? 'center' : 'top';
                },
                anchor: function(context) {
                    return ['pie', 'doughnut'].includes(baseType) ? 'center' : 'end';
                },
                
                formatter: function(value, context) {
                    if (['pie', 'doughnut'].includes(baseType)) {
                        const val = value !== undefined ? value : 0;
                        const dataset = context.dataset.data;
                        const total = dataset.reduce((sum, current) => sum + current, 0);
                        const percentage = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                        return Number(val).toLocaleString() + '\n(' + percentage + '%)';
                    }
                    if (['mr_bubble', 'mr_scatter'].includes(styleMeta)) {
                        const rating = (value && value.y !== undefined) ? value.y : context.raw;
                        if (rating) {
                            return rating + ' ★';
                        }
                    }
                    
                    return ['bar', 'line'].includes(baseType) ? Number(value).toLocaleString() : '';
                },
                font: {
                    weight: 'bold',
                    size: 11
                },
                color: function(context) {
                    return ['pie', 'doughnut'].includes(baseType) ? '#ffffff' : '#333333';
                },
                textAlign: 'center',
                offset: function(context) {
                    return ['pie', 'doughnut'].includes(baseType) ? 0 : 4;
                }
            },
            tooltip: {
                callbacks: {
                    title: function(context) {
                        return context[0].dataset.label;
                    },
                    label: function(context) {
                        if (['mr_bubble', 'mr_scatter'].includes(styleMeta)) {
                            const rawPoint = context.raw;
                            if (rawPoint && rawPoint.y !== undefined) {
                                let info = 'Điểm: ' + rawPoint.y + ' ★';
                                if (rawPoint.r) info += ' (Sản lượng: ' + rawPoint.r + ' bản)';
                                return info;
                            }
                        }

                        if (['radar', 'polarArea', 'pie', 'doughnut'].includes(baseType)) {
                            const label = context.label || '';
                            const val = context.raw !== undefined ? context.raw : 0; 
                            const dataset = context.dataset.data;
                            const total = dataset.reduce((sum, current) => sum + current, 0);
                            const percentage = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                            return label + ': ' + Number(val).toLocaleString() + ' (' + percentage + '%)';
                        }
                        
                        if (styleMeta === 'horizontal') {
                            const label = context.label || '';
                            const val = context.parsed.x !== undefined ? context.parsed.x : context.raw;
                            return label + ': ' + Number(val).toLocaleString() + ' VNĐ';
                        }
                        
                        const datasetLabel = context.dataset.label || '';
                        const valY = context.parsed.y;
                        if (datasetLabel.includes("Giá")) {
                            return datasetLabel + ': ' + Number(valY).toLocaleString() + ' VNĐ';
                        }
                        return datasetLabel + ': ' + Number(valY).toLocaleString();
                    }
                }
            }
        },
        scales: { x: {}, y: {} }
    }

    if (styleMeta === 'spark_full_columns' || styleMeta === 'spark_multi_axis') {
        options.scales = {
            x: {},
            y_volume: {
                type: 'linear',
                position: 'left',
                title: { display: true, text: 'Tổng sản lượng bán (Sách)' },
                ticks: { callback: value => value.toLocaleString() }
            },
            y_right_count: {
                type: 'linear',
                position: 'right',
                title: { display: true, text: 'Số lượng đầu sách (Cuốn)' },
                grid: { drawOnChartArea: false }, // Tắt lưới 
                ticks: { callback: value => value.toLocaleString() }
            }
        };
        
        if (styleMeta === 'spark_full_columns') {
            options.scales.y_price = {
                type: 'linear',
                position: 'right',
                title: { display: true, text: 'Giá trung bình (VNĐ)' },
                grid: { drawOnChartArea: false },
                ticks: { callback: value => value.toLocaleString() }
            };
            options.scales.y_rating = {
                type: 'linear',
                position: 'right',
                min: 0,
                max: 6.0, 
                title: { display: true, text: 'Rating (★)' },
                grid: { drawOnChartArea: false },
                weight: 2 
            };
        }

        if (options.scales.y) {
            delete options.scales.y;
        }
    }
    else if (['mr_bubble', 'mr_scatter'].includes(styleMeta)) {
        options.scales = {
            x: { title: { display: true, text: 'Thứ tự mẫu dữ liệu phân tích' } },
            y: { min: 0, max: 6.0, title: { display: true, text: 'Điểm đánh giá (Sao)' } }
        };
    } else {
        options.scales = {
            x: {},
            y: {
                beginAtZero: true,
                grace: '15%', 
                ticks: {
                    callback: function(value) { return value.toLocaleString(); }
                }
            }
        };
        if (styleMeta === 'horizontal') { options.indexAxis = 'y'; options.scales.x = { grace: '15%' };
            options.scales.y = { beginAtZero: true };}
        if (['pie', 'doughnut', 'polarArea', 'radar'].includes(baseType)) { delete options.scales; }
    }

    if (['mr_bubble', 'mr_scatter'].includes(styleMeta) && payload.data && payload.data.datasets && payload.data.datasets.length > 0) {
        const originalDataset = payload.data.datasets[0]; 
        const dataPoints = originalDataset.data;
        const labels = payload.data.labels || [];
        const newDatasets = [];
        const dataLength = dataPoints.length;

        for (let i = 0; i < dataLength; i++) {
            const hue = (i * (360 / dataLength)) % 360;
            const pointColor = `hsla(${hue}, 75%, 55%, 0.85)`;
            const bookName = labels[i] || `Mẫu dữ liệu ${i + 1}`;

            newDatasets.push({
                label: bookName, 
                data: [dataPoints[i]], 
                backgroundColor: pointColor,
                borderColor: pointColor,
                pointBackgroundColor: pointColor,
                pointRadius: styleMeta === 'mr_bubble' ? undefined : 8, 
                hoverRadius: 12
            });
        }
        payload.data.datasets = newDatasets; 
    }

    if (window.myChartInstance && typeof window.myChartInstance.destroy === 'function') { 
        window.myChartInstance.destroy(); 
    }

    const activePlugins = [];
    
    if (typeof ChartDataLabels !== 'undefined') {
        activePlugins.push(ChartDataLabels);
    } else if (typeof window.ChartDataLabels !== 'undefined') {
        activePlugins.push(window.ChartDataLabels);
    } else {
        console.warn("Chú ý: Chưa tìm thấy thư viện ChartDataLabels từ CDN, biểu đồ sẽ vẽ mà chưa có chữ nổi.");
    }
    
    window.myChartInstance = new Chart(ctx, {
        type: baseType === 'horizontalBar' ? 'bar' : baseType,
        data: payload.data,
        options: options,
        plugins: activePlugins
    });
}

function renderBarChart(canvasId, chartData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !chartData) return;

    const ctx = canvas.getContext('2d');
    
    if (window.myQualityChartInstance) {
        window.myQualityChartInstance.destroy();
    }

    window.myQualityChartInstance = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }, 
                title: {
                    display: true,
                    text: 'Thống kê kiểm định chất lượng dữ liệu đầu vào (HDFS)',
                    font: { size: 14, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Số lượng dòng dữ liệu (Records)' },
                    ticks: { callback: value => value.toLocaleString() } 
                },
                x: {
                    title: { display: true, text: 'Tiêu chí kiểm định chất lượng' }
                }
            }
        }
    });
}

function showPageNotice(message, variant = "success") {
  const container = document.getElementById("pageNotices");
  if (!container) {
    return;
  }
  container.innerHTML = `
    <div class="alert alert-${variant} alert-dismissible fade show" role="alert">
      ${escapeHtml(message)}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Đóng"></button>
    </div>
  `;
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value ?? "";
  return element.innerHTML;
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") {
    return "Chưa có";
  }
  return new Intl.NumberFormat("vi-VN").format(value);
}

function labelForField(field) {
  return {
    book_id: "Book ID",
    source: "Nguồn",
    title: "Tên sách",
    author: "Tác giả",
    publisher: "Nhà xuất bản",
    language_group: "Nhóm ngôn ngữ",
    main_category: "Category lớn",
    sub_category: "Sub-category",
    price: "Giá bán",
    original_price: "Giá gốc",
    discount_rate: "Giảm giá",
    rating: "Rating",
    review_count: "Lượt đánh giá",
    sold_count: "Đã bán",
    publish_year: "Năm xuất bản",
    page_count: "Số trang",
    url: "URL"
  }[field] || field;
}

function detailValue(field, value) {
  if (field === "price" || field === "original_price") {
    return `${formatNumber(value)} đ`;
  }
  if (field === "discount_rate") {
    return `${formatNumber(value)}%`;
  }
  if (field === "url" && value) {
    return `<a href="${escapeHtml(value)}" target="_blank" rel="noopener noreferrer">Mở trang sản phẩm</a>`;
  }
  return escapeHtml(value ?? "Chưa có");
}

function resetBookForm(form) {
  form.reset();
  form.classList.remove("was-validated");
  form.querySelectorAll(".is-invalid").forEach((field) => field.classList.remove("is-invalid"));
  form.querySelectorAll("[data-error-for]").forEach((element) => {
    element.textContent = "";
  });
  const errorBox = document.getElementById("bookFormError");
  errorBox?.classList.add("d-none");
  if (errorBox) {
    errorBox.textContent = "";
  }
  ["price", "original_price", "discount_rate", "rating", "review_count", "sold_count"].forEach((name) => {
    const field = form.elements.namedItem(name);
    if (field) {
      field.value = "0";
    }
  });
  form.dataset.operation = "create";
  form.dataset.originalSource = "";
  form.dataset.originalBookId = "";
  form.elements.namedItem("book_id").readOnly = false;
  form.elements.namedItem("source").disabled = false;
}

function fillBookForm(form, book) {
  Object.entries(book).forEach(([name, value]) => {
    const field = form.elements.namedItem(name);
    if (field) {
      field.value = value ?? "";
    }
  });
}

function showBookErrors(form, errors, fallbackMessage) {
  form.classList.remove("was-validated");

  const errorBox = document.getElementById("bookFormError");
  if (errorBox) {
    errorBox.textContent = fallbackMessage;
    errorBox.classList.remove("d-none");
    errorBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  Object.entries(errors || {}).forEach(([name, message]) => {
    const field = form.elements.namedItem(name);
    const feedback = form.querySelector(`[data-error-for="${name}"]`);
    
    if (field) {
      field.classList.remove("is-valid"); 
      field.classList.add("is-invalid");    
    }
    
    if (feedback) {
      feedback.textContent = message;
    }
  });
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.message || "Không thể xử lý yêu cầu.");
    error.payload = payload;
    throw error;
  }
  return payload;
}

function initializeCategoryFilters() {
  const mainSelect = document.getElementById("mainCategoryFilter");
  const subSelect = document.getElementById("subCategoryFilter");
  const treeElement = document.getElementById("bookCategoryTree");
  if (!mainSelect || !subSelect || !treeElement) {
    return;
  }

  let categoryTree = {};
  try {
    categoryTree = JSON.parse(treeElement.textContent);
  } catch {
    return;
  }

  const renderSubCategories = (selectedValue = "") => {
    const mainCategory = mainSelect.value;
    const subCategories = categoryTree[mainCategory] || [];
    subSelect.replaceChildren();

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = mainCategory
      ? "Tất cả danh mục phụ"
      : "Chọn danh mục lớn trước";
    subSelect.append(defaultOption);

    subCategories.forEach((subCategory) => {
      const option = document.createElement("option");
      option.value = subCategory;
      option.textContent = subCategory;
      option.selected = subCategory === selectedValue;
      subSelect.append(option);
    });
    subSelect.disabled = !mainCategory;
    subSelect.title = subSelect.selectedOptions[0]?.textContent || "";
  };

  mainSelect.title = mainSelect.selectedOptions[0]?.textContent || "";
  renderSubCategories(subSelect.dataset.selectedValue || "");
  mainSelect.addEventListener("change", () => {
    mainSelect.title = mainSelect.selectedOptions[0]?.textContent || "";
    renderSubCategories();
  });
  subSelect.addEventListener("change", () => {
    subSelect.title = subSelect.selectedOptions[0]?.textContent || "";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initializeCategoryFilters();
  let lastFocusedPriceField = "";

  const savedNotice = sessionStorage.getItem("bookPageNotice");
  if (savedNotice) {
    showPageNotice(savedNotice);
    sessionStorage.removeItem("bookPageNotice");
  }

  const form = document.getElementById("bookModalForm");
  const detailElement = document.getElementById("bookDetailModal");
  const formElement = document.getElementById("bookFormModal");
  const deleteElement = document.getElementById("deleteBookModal");

  if (!form || typeof bootstrap === "undefined") {
    return;
  }

  const detailModal = detailElement ? new bootstrap.Modal(detailElement) : null;
  const formModal = formElement ? new bootstrap.Modal(formElement) : null;
  const deleteModal = deleteElement ? new bootstrap.Modal(deleteElement) : null;

  document.getElementById("openAddBookButton")?.addEventListener("click", () => {
    resetBookForm(form);
    document.getElementById("bookFormModalTitle").textContent = "Thêm sách";
    formModal?.show();
  });

  document.querySelectorAll(".js-view-book").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const { book } = await fetchJson(button.dataset.apiUrl);
        document.getElementById("detailTitle").textContent = book.title;
        const detailGrid = document.getElementById("bookDetailGrid");
        detailGrid.innerHTML = Object.entries(book)
          .filter(([field]) => field !== "row_key")
          .map(([field, value]) => `
            <div class="col-md-6">
              <div class="detail-item">
                <div class="detail-label">${escapeHtml(labelForField(field))}</div>
                <div class="detail-value">${detailValue(field, value)}</div>
              </div>
            </div>
          `)
          .join("");
        detailModal?.show();
      } catch (error) {
        showPageNotice(error.message, "danger");
      }
    });
  });

  document.querySelectorAll(".js-edit-book").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const { book } = await fetchJson(button.dataset.apiUrl);
        resetBookForm(form);
        fillBookForm(form, book);
        form.dataset.operation = "update";
        form.dataset.originalSource = book.source;
        form.dataset.originalBookId = book.book_id;
        form.elements.namedItem("book_id").readOnly = true;
        form.elements.namedItem("source").disabled = true;
        document.getElementById("bookFormModalTitle").textContent = "Cập nhật sách";
        formModal?.show();
      } catch (error) {
        showPageNotice(error.message, "danger");
      }
    });
  });

  form.elements.namedItem("price")?.addEventListener("input", () => {
    lastFocusedPriceField = "price";
  });
  form.elements.namedItem("original_price")?.addEventListener("input", () => {
    lastFocusedPriceField = "original_price";
  });
  form.elements.namedItem("discount_rate")?.addEventListener("input", () => {
    lastFocusedPriceField = "discount_rate";
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    form.classList.add("was-validated");
    form.querySelectorAll(".is-invalid").forEach((field) => field.classList.remove("is-invalid"));
    if (!form.checkValidity()) {
      showBookErrors(form, {}, "Vui lòng kiểm tra các trường bắt buộc và giới hạn giá trị.");
      return;
    }

    const payload = Object.fromEntries(new FormData(form).entries());
    payload.source = form.elements.namedItem("source").value;
    payload._last_focused_field = lastFocusedPriceField;
    payload._operation = form.dataset.operation || "create";
    payload._original_source = form.dataset.originalSource || "";
    payload._original_book_id = form.dataset.originalBookId || "";
    try {
      const result = await fetchJson("/api/books", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      sessionStorage.setItem("bookPageNotice", result.message);
      window.location.reload();
    } catch (error) {
      showBookErrors(form, error.payload?.errors, error.message);
    }
  });

  const deleteCheckbox = document.getElementById("deleteConfirmation");
  const deleteButton = document.getElementById("confirmDeleteBookButton");
  let deleteUrl = "";

  document.querySelectorAll(".js-delete-book").forEach((button) => {
    button.addEventListener("click", () => {
      deleteUrl = button.dataset.deleteUrl;
      document.getElementById("deleteBookTitle").textContent = button.dataset.bookTitle;
      document.getElementById("deleteBookError").classList.add("d-none");
      deleteCheckbox.checked = false;
      deleteButton.disabled = true;
      deleteModal?.show();
    });
  });

  deleteCheckbox?.addEventListener("change", () => {
    deleteButton.disabled = !deleteCheckbox.checked;
  });

  deleteButton?.addEventListener("click", async () => {
    if (!deleteCheckbox.checked || !deleteUrl) {
      return;
    }
    try {
      const result = await fetchJson(deleteUrl, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirm: true })
      });
      sessionStorage.setItem("bookPageNotice", result.message);
      window.location.reload();
    } catch (error) {
      const errorBox = document.getElementById("deleteBookError");
      errorBox.textContent = error.message;
      errorBox.classList.remove("d-none");
    }
  });
});