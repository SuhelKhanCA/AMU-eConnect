document.addEventListener("DOMContentLoaded", function () {
  let department = "";
  let course = "";
  let year_of_passing = "";
  const searchButton = document.getElementById("searchButton");
  const searchInput = document.getElementById("searchInput");

  // Dropdown item event listeners
  document.querySelectorAll(".department-item").forEach((item) => {
    item.addEventListener("click", function () {
      department = this.getAttribute("data-value");
    });
  });

  document.querySelectorAll(".course-item").forEach((item) => {
    item.addEventListener("click", function () {
      course = this.getAttribute("data-value");
    });
  });

  document.querySelectorAll(".year-item").forEach((item) => {
    item.addEventListener("click", function () {
      year_of_passing = this.getAttribute("data-value");
    });
  });

  // Search button click handler
  searchButton.addEventListener("click", function () {
    const search_term = searchInput.value;

    fetch("/filter_cards", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        department: department,
        course: course,
        year_of_passing: year_of_passing,
        search_term: search_term,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const cardsContainer = document.getElementById("cardsContainer");
        cardsContainer.innerHTML = "";

        if (data.length === 0) {
          cardsContainer.innerHTML = "<p>No results found.</p>";
        } else {
          data.forEach((card) => {
            cardsContainer.innerHTML += `
                            <div class="col">
                                <div class="card h-100">
                                    <img src="data:image/jpeg;base64,${card.user_image}" class="card-img-top img-fluid d-block w-100" style="height: 300px" alt="${card.name}" />
                                    <div class="card-body">
                                        <h5 class="card-title">${card.name}</h5>
                                        <p class="card-text">${card.course} - ${card.department} (${card.passing_year})</p>
                                        <p>{{cards.short_desc}}</p>
                                    </div>
                                <a href="/profile/${card.id}" class="btn btn-dark mb-1">View Profile</a>    
                                </div>
                            </div>
                        `;
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("cardsContainer").innerHTML =
          "<p>There was an error processing the request.</p>";
      });
  });
});
