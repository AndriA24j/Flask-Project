const categories = document.getElementsByClassName("category");

for (let i = 0; i < categories.length; i++) {
  const header = categories[i].querySelector(".category-header");

  header.addEventListener("click", function () {
    // Close all other categories
    for (let j = 0; j < categories.length; j++) {
      if (j !== i) {
        categories[j].classList.remove("active");
      }
    }

    // Toggle current category
    categories[i].classList.toggle("active");
  });
}

const nav = document.querySelector(".navdiv");
const navToggle = document.querySelector(".nav-toggle");
const navPanel = document.querySelector(".nav-panel");

if (nav && navToggle && navPanel) {
  const setNavState = (isOpen) => {
    nav.classList.toggle("nav-open", isOpen);
    navToggle.setAttribute("aria-expanded", String(isOpen));
  };

  navToggle.addEventListener("click", function () {
    const isOpen = nav.classList.contains("nav-open");
    setNavState(!isOpen);
  });

  navPanel.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      setNavState(false);
    });
  });

  document.addEventListener("click", function (event) {
    if (!nav.contains(event.target)) {
      setNavState(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setNavState(false);
    }
  });
}

let qtyInput = document.getElementById("qty");

function increaseQty() {
  let qty = parseInt(qtyInput.value);
  qty++;
  qtyInput.value = qty;
}

function decreaseQty() {
  let qty = parseInt(qtyInput.value);
  if (qty > 1) {
    qty--;
    qtyInput.value = qty;
  }
}


