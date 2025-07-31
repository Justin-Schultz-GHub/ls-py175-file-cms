"use strict";

document.addEventListener("DOMContentLoaded", function () {
  let deleteFile = document.querySelectorAll(".delete");
  deleteFile.forEach(link => {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();

      if (confirm(
                `Are you sure you want to delete this file?
                This cannot be undone!`
                )) {

        window.location = link.href;
      }
    });
  });
});
