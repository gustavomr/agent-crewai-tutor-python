chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: clickRepeatedDropdowns
    });
  });
  
  function clickRepeatedDropdowns() {
    const dropdownWrappers = document.querySelectorAll('.c-ierzuX');
  
    dropdownWrappers.forEach((wrapper, i) => {
      setTimeout(() => {
        // Click the wrapper to open the dropdown
        wrapper.click();
        console.log(`Dropdown ${i + 1} clicked`);
  
        // Then wait and click the first visible option (can change index if needed)
        setTimeout(() => {
          const options = document.querySelectorAll('.c-cKuoTs');
          if (options.length > 0) {
            options[0].click(); // or options[1] for second option
            if (i === 5) {
                options[2].click();
            }
            console.log(`Option clicked for dropdown ${i + 1}`);
          } else {
            console.warn(`No options found for dropdown ${i + 1}`);
          }
        }, 400); // short wait for options to appear
      }, i * 1000); // staggered execution to avoid collisions
    });
  }
  