$(document).ready(function() {
    let records = [];
    let filteredRecords = [];
    let currentIndex = 0;
    let originalRecords = [];

    // Google Drive URL for the CSV file
    const sheetUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent('https://docs.google.com/spreadsheets/d/1iE1BrdJK4A-k5XNi_fRkR5FQ7YgS5MTJv-1A_v2aAxg/export?format=csv');

    // Function to fetch and parse CSV data
    function fetchCSV(url) {
        return new Promise((resolve, reject) => {
            $.get(url, function(response) {
                const base64Index = response.contents.indexOf('base64,') + 'base64,'.length;
                const decodedData = atob(response.contents.substring(base64Index));

                Papa.parse(decodedData, {
                    header: true,
                    complete: function(results) {
                        resolve(results.data);
                    },
                    error: function(error) {
                        reject(error);
                    }
                });
            }).fail(function(error) {
                reject(error);
            });
        });
    }

    // Load and display the data
    fetchCSV(sheetUrl).then(data => {
        originalRecords = data;
        records = [...originalRecords];
        filteredRecords = records;
        console.log("Records loaded:", records); // Debugging: Log the loaded records
        displayRecord(currentIndex);
    }).catch(error => {
        console.error('Error loading data:', error);
    });

    // Function to display a record
    function displayRecord(index) {
        const record = filteredRecords[index];
        if (!record) return;

        console.log("Displaying record:", record); // Debugging: Log the record being displayed

        $("#record-display").html(`
            <h3>${record['Company Name']}</h3>
            <p><strong>Analysis Year:</strong> ${record['Analysis Year']}</p>
            <p><strong>AIM Category:</strong> ${record['AIM Category']}</p>
            <p><strong>Revenue Share Analysis:</strong> ${formatCollapsibleText(record['Revenue Share Analysis '], "revenue-share")}</p>
            <p><strong>Review Status:</strong> ${record['Review Status']}</p>
            <p><strong>Pending Review Comments:</strong> ${record['Pending Review Comments']}</p>
            <p><strong>Basic Industry (Basic_Ind_Code):</strong></p>
            <table id="basic-industry-table">
                <tr>
                    <th>Sector</th>
                    <th>NSE Basic Industry</th>
                    <th>Revenue Share</th>
                    <th>Justification</th>
                </tr>
                ${formatBasicIndustry(record['Basic Industry (Basic_Ind_Code)'])}
            </table>
            <p><strong>BWC 2017 Category:</strong> ${record['BWC 2017 Category']}</p>
            <p><strong>Activities from BWC Guide:</strong> ${record['Activities from BWC Guide']}</p>
        `);

        $("#prev").prop("disabled", index <= 0);
        $("#next").prop("disabled", index >= filteredRecords.length - 1);

        // Attach click event to show more/less
        $(".show-more").off("click").on("click", function() {
            console.log("Show more clicked"); // Debugging: Log when "Show more" is clicked
            const content = $(this).prev(".collapsible-content");
            content.toggle();
            $(this).text(content.is(":visible") ? "Show less" : "Show more");
        });
    }

    // Format text into a collapsible structure
    function formatCollapsibleText(text, className = "") {
        console.log("Formatting text for collapsible content:", text); // Debugging: Log the text being formatted
        if (!text || text === "undefined") return 'N/A';
        const words = text.split(' ');
        if (words.length > 10) {
            const visibleText = words.slice(0, 10).join(' ');
            const hiddenText = words.slice(10).join(' ');
            return `${visibleText}... <span class="show-more ${className}" style="color: blue; cursor: pointer;">Show more</span><span class="collapsible-content ${className}" style="display:none;"> ${hiddenText}</span>`;
        } else {
            return text;
        }
    }

    // Format "Basic Industry" field into a table with collapsible "Justification" column
    function formatBasicIndustry(data) {
        console.log("Formatting Basic Industry data:", data); // Debugging: Log the data being formatted
        if (!data || data === "undefined") return '<tr><td colspan="4">N/A</td></tr>';
        return data.split('\n').map(line => {
            const [sector, industry, share, justification] = line.split('|');
            return `
                <tr>
                    <td>${sector}</td>
                    <td>${industry}</td>
                    <td>${share}</td>
                    <td>${formatCollapsibleText(justification, "industry-justification")}</td>
                </tr>
            `;
        }).join('');
    }

    // Navigation buttons
    $("#prev").click(function() {
        if (currentIndex > 0) {
            currentIndex--;
            displayRecord(currentIndex);
        }
    });

    $("#next").click(function() {
        if (currentIndex < filteredRecords.length - 1) {
            currentIndex++;
            displayRecord(currentIndex);
        }
    });

    // Search functionality
    $("#search").on("input", function() {
        const query = $(this).val().toLowerCase();
        filteredRecords = originalRecords.filter(record =>
            record['Company Name'].toLowerCase().includes(query)
        );
        console.log("Search results:", filteredRecords); // Debugging: Log the filtered records after search
        currentIndex = 0;
        displayRecord(currentIndex);
    });
});
