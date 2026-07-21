(function () {
  const trees = document.querySelectorAll(
    "[data-category-index-tree]"
  );

  if (trees.length === 0) {
    return;
  }

  trees.forEach(tree => {
    tree.addEventListener("click", event => {
      const button = event.target.closest(
        ".category-index-tree__toggle"
      );

      if (!button || !tree.contains(button)) {
        return;
      }

      const item = button.closest(
        ".category-index-tree__item"
      );

      if (!item) {
        return;
      }

      const children = Array.from(item.children).find(
        element =>
          element.classList.contains(
            "category-index-tree__children"
          )
      );

      if (!children) {
        return;
      }

      const isExpanded =
        button.getAttribute("aria-expanded") === "true";

      button.setAttribute(
        "aria-expanded",
        isExpanded ? "false" : "true"
      );

      children.hidden = isExpanded;
    });
  });
})();