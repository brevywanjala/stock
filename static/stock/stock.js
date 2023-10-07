$(document).ready(function() {
    // Search input field for students
    var studentSearchInput = $('#student-search-input input[type="text"]');

    // Autocomplete suggestions dropdown for students
    var studentSuggestionsDropdown = $('#student-suggestions');

    // Event handler for input changes in student search field
    studentSearchInput.on('input', function() {
        var studentQuery = $(this).val();

        // Clear previous student suggestions
        studentSuggestionsDropdown.empty();

        // Make AJAX request to get matching student names
        $.ajax({
            url: '/get_students',
            method: 'GET',
            data: {
                query: studentQuery
            },
            success: function(studentResponse) {
                // Display the student suggestions dropdown if there are matching students
                if (studentResponse.length > 0) {
                    studentSuggestionsDropdown.show();
                } else {
                    studentSuggestionsDropdown.hide();
                }

                // Add the matching student names to the suggestions dropdown
                for (var i = 0; i < studentResponse.length; i++) {
                    studentSuggestionsDropdown.append('<li>' + studentResponse[i] + '</li>');
                }
            }
        });
    });

    // Event handler for selecting a student suggestion
    studentSuggestionsDropdown.on('click', 'li', function() {
        var selectedStudent = $(this).text();

        // Set the selected student as the input value
        studentSearchInput.val(selectedStudent);

        // Hide the student suggestions dropdown
        studentSuggestionsDropdown.hide();

        // Make an AJAX request to fetch picked items for the selected student
        $.ajax({
            url: '/get_picked_items',
            method: 'GET',
            data: {
                student_name: selectedStudent
            },
            success: function(response) {
                // Display the picked items and dates in a list
                $('#picked-items-container').show();
              $('#selected-student').text(selectedStudent);
              $('#picked-items-list').empty();
              if (response.length > 0) {
                  var itemsHtml = '';
                  response.forEach(function(item) {
                      itemsHtml += '<tr><td>' + item.item_name + '</td><td>' + item.pick_date + '</td></tr>';
                  });
                  $('#picked-items-list').html(itemsHtml);
              } else {
                  $('#picked-items-list').html('<tr><td colspan="2">No items picked by this student.</td></tr>');
              }
            }
        });
    });

    // ... (your existing code for items autocomplete)
});


$(document).ready(function() {
    // Search input field
    var searchInput = $('#item-search-input input[type="text"]');

    // Autocomplete suggestions dropdown
    var suggestionsDropdown = $('#item-suggestions');

    // Event handler for input changes in search field
    searchInput.on('input', function() {
        var query = $(this).val();

        // Clear previous suggestions
        suggestionsDropdown.empty();

        // Make AJAX request to get matching item names
        $.ajax({
            url: '/get_items',
            method: 'GET',
            data: {
                query: query
            },
            success: function(response) {
                // Display the suggestions dropdown if there are matching items
                if (response.length > 0) {
                    suggestionsDropdown.show();
                } else {
                    suggestionsDropdown.hide();
                }

                // Add the matching item names to the suggestions dropdown
                for (var i = 0; i < response.length; i++) {
                    suggestionsDropdown.append('<li>' + response[i] + '</li>');
                }
            }
        });
    });

    // Event handler for selecting a suggestion
    suggestionsDropdown.on('click', 'li', function() {
        var selectedSuggestion = $(this).text();

        // Set the selected suggestion as the input value
        searchInput.val(selectedSuggestion);

        // Hide the suggestions dropdown
        suggestionsDropdown.hide();

        // Make an AJAX request to fetch item details
        $.ajax({
            url: '/get_item_details',
            method: 'GET',
            data: {
                item_name: selectedSuggestion
            },
            success: function(response) {
                if (response) {
                    // Fill in the item details in the form
                    $('#item-name').val(response.item_name);
                    $('#item-quantity').val(response.quantity);
                    $('#item-days').val(response.days_to_next_pick);
                    $('#item-threshold').val(response.quantity_threshold);
                }
            }
        });
    });
});
