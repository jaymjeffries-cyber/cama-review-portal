"""
MLS Matrix - Custom Workflow with Native Export (Google Colab Version)
Uses MLS Matrix's built-in export to CSV functionality
Workflow: Login → Matrix → Saved Searches → CAMAvsMLS → Results → Check All → Export as C3 CSV

SETUP INSTRUCTIONS FOR GOOGLE COLAB:
1. Run the setup cell below FIRST
2. Then run this script
"""

# ============================================================================
# SETUP CELL - RUN THIS FIRST IN COLAB
# ============================================================================
"""
# Paste this in the FIRST cell of your Colab notebook:

!pip install -q selenium
!apt-get update > /dev/null 2>&1
!apt install -y chromium-chromedriver > /dev/null 2>&1
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
print("✅ Setup complete!")
"""

# ============================================================================
# MAIN SCRIPT - RUN THIS IN THE SECOND CELL
# ============================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time


class CustomMLSExporter:
    def __init__(self):
        """Initialize the custom exporter with Colab-specific options"""
        print("🚀 Starting browser...")
        
        # Configure Chrome for Colab environment
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Must run headless in Colab
        chrome_options.add_argument("--no-sandbox")  # Required for Colab
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--disable-gpu")  # Disable GPU
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set download directory to Colab's working directory
        prefs = {
            "download.default_directory": "/content",
            "download.prompt_for_download": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        print("✅ Browser started successfully!")
        
    def login(self, username, password):
        """Step 1: Login to MLS Matrix"""
        print("\n" + "="*70)
        print("STEP 1: LOGIN")
        print("="*70)
        
        self.driver.get("https://now.mlsmatrix.com")
        time.sleep(3)
        
        try:
            # Try common login patterns
            try:
                username_field = self.driver.find_element(By.ID, "loginUsername")
                password_field = self.driver.find_element(By.ID, "loginPassword")
                login_button = self.driver.find_element(By.ID, "loginButton")
            except:
                username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            login_button.click()
            time.sleep(5)
            
            print("✅ Login successful!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def click_matrix_icon(self):
        """Step 2: Click on the Matrix icon to enter Matrix application"""
        print("\n" + "="*70)
        print("STEP 2: CLICK MATRIX ICON")
        print("="*70)
        
        try:
            # Wait longer for page to fully load after login
            print("   Waiting for page to load after login...")
            time.sleep(5)
            
            matrix_clicked = False
            
            # Method 1: By exact ID
            print("   Method 1: Trying by ID='1'...")
            try:
                matrix_icon = self.wait.until(
                    EC.presence_of_element_located((By.ID, "1"))
                )
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView(true);", matrix_icon)
                time.sleep(1)
                
                # Try regular click
                try:
                    matrix_icon.click()
                    matrix_clicked = True
                    print("✅ Clicked Matrix icon (by ID - regular click)")
                except:
                    # Try JavaScript click if regular click fails
                    self.driver.execute_script("arguments[0].click();", matrix_icon)
                    matrix_clicked = True
                    print("✅ Clicked Matrix icon (by ID - JS click)")
                    
            except Exception as e:
                print(f"   Method 1 failed: {str(e)[:100]}")
            
            # Method 2: By image source
            if not matrix_clicked:
                print("   Method 2: Trying by image source...")
                try:
                    matrix_icon = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "img[src*='CoreLogicMatrix']"
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", matrix_icon)
                    time.sleep(1)
                    
                    try:
                        matrix_icon.click()
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by src - regular click)")
                    except:
                        self.driver.execute_script("arguments[0].click();", matrix_icon)
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by src - JS click)")
                        
                except Exception as e:
                    print(f"   Method 2 failed: {str(e)[:100]}")
            
            # Method 3: By title
            if not matrix_clicked:
                print("   Method 3: Trying by title...")
                try:
                    matrix_icon = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "img[title='Matrix']"
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", matrix_icon)
                    time.sleep(1)
                    
                    try:
                        matrix_icon.click()
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by title - regular click)")
                    except:
                        self.driver.execute_script("arguments[0].click();", matrix_icon)
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by title - JS click)")
                        
                except Exception as e:
                    print(f"   Method 3 failed: {str(e)[:100]}")
            
            # Method 4: By alt
            if not matrix_clicked:
                print("   Method 4: Trying by alt attribute...")
                try:
                    matrix_icon = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "img[alt='Matrix']"
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", matrix_icon)
                    time.sleep(1)
                    
                    try:
                        matrix_icon.click()
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by alt - regular click)")
                    except:
                        self.driver.execute_script("arguments[0].click();", matrix_icon)
                        matrix_clicked = True
                        print("✅ Clicked Matrix icon (by alt - JS click)")
                        
                except Exception as e:
                    print(f"   Method 4 failed: {str(e)[:100]}")
            
            # Method 5: Search all images
            if not matrix_clicked:
                print("   Method 5: Searching all images for 'matrix'...")
                try:
                    all_images = self.driver.find_elements(By.TAG_NAME, "img")
                    for img in all_images:
                        try:
                            src = img.get_attribute("src") or ""
                            alt = img.get_attribute("alt") or ""
                            title = img.get_attribute("title") or ""
                            
                            if "matrix" in src.lower() or "matrix" in alt.lower() or "matrix" in title.lower():
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", img)
                                time.sleep(1)
                                
                                try:
                                    img.click()
                                    matrix_clicked = True
                                    print("✅ Clicked Matrix icon (found by searching images)")
                                    break
                                except:
                                    self.driver.execute_script("arguments[0].click();", img)
                                    matrix_clicked = True
                                    print("✅ Clicked Matrix icon (found by searching images - JS)")
                                    break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"   Method 5 failed: {str(e)[:100]}")
            
            if not matrix_clicked:
                print("\n❌ Could not find Matrix icon after trying all methods")
                self.driver.save_screenshot("/content/after_login_no_matrix.png")
                
                # Print page info for debugging
                print(f"   Current URL: {self.driver.current_url}")
                print(f"   Page title: {self.driver.title}")
                
                # Try to save page source
                try:
                    with open("/content/after_login_page_source.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("   Page source saved to: /content/after_login_page_source.html")
                except:
                    pass
                
                return False
            
            # Wait for next page to load
            time.sleep(5)
            print("✅ Matrix application loaded")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking Matrix icon: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_saved_searches(self):
        """Step 3: Navigate to Saved Searches via My Matrix menu"""
        print("\n" + "="*70)
        print("STEP 3: NAVIGATE TO SAVED SEARCHES")
        print("="*70)
        
        try:
            time.sleep(2)
            
            # Now we're on the Matrix page, find "My Matrix" menu
            print("   Looking for 'My Matrix' menu...")
            
            my_matrix = None
            selectors = [
                "//span[@class='text-uppercase' and contains(text(), 'My Matrix')]",
                "//span[contains(text(), 'My Matrix')]",
                "//*[contains(text(), 'My Matrix')]",
                "//a[contains(text(), 'My Matrix')]"
            ]
            
            for selector in selectors:
                try:
                    my_matrix = self.driver.find_element(By.XPATH, selector)
                    print(f"   Found 'My Matrix'")
                    break
                except:
                    continue
            
            if not my_matrix:
                print("❌ Could not find 'My Matrix' menu")
                self.driver.save_screenshot("/content/my_matrix_not_found.png")
                return False
            
            print("   Hovering over 'My Matrix'...")
            actions = ActionChains(self.driver)
            actions.move_to_element(my_matrix).perform()
            
            # Wait longer for submenu to appear and fully render
            print("   Waiting for submenu to appear...")
            time.sleep(4)
            
            # DEBUG: List all visible links in the dropdown
            try:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                print(f"   DEBUG: Found {len(all_links)} total links on page")
                
                # Filter for links that might be in the dropdown (visible and contain relevant text)
                dropdown_links = []
                for link in all_links:
                    try:
                        if link.is_displayed():
                            text = link.text.strip()
                            href = link.get_attribute("href") or ""
                            if text and ("Saved" in text or "Search" in text or "Matrix" in text):
                                dropdown_links.append(f"{text} -> {href}")
                    except:
                        pass
                
                if dropdown_links:
                    print("   DEBUG: Dropdown links found:")
                    for link_info in dropdown_links[:10]:  # Show first 10
                        print(f"      - {link_info}")
            except Exception as debug_err:
                print(f"   DEBUG: Could not list links: {debug_err}")
            
            print("   Looking for 'My Saved Searches' link...")
            
            # Try multiple ways to find and click "My Saved Searches"
            link_selectors = [
                # Method 1: By exact href
                (By.CSS_SELECTOR, "a[href='/Matrix/SavedSearches']", "exact href /Matrix/SavedSearches"),
                # Method 2: By href with .aspx
                (By.CSS_SELECTOR, "a[href='/Matrix/SavedSearches.aspx']", "href with .aspx"),
                # Method 3: By href containing SavedSearches
                (By.CSS_SELECTOR, "a[href*='SavedSearches']", "href contains SavedSearches"),
                # Method 4: By text content
                (By.XPATH, "//a[contains(text(), 'My Saved Searches')]", "text contains 'My Saved Searches'"),
                # Method 5: By partial text
                (By.XPATH, "//a[contains(text(), 'Saved Searches')]", "text contains 'Saved Searches'"),
                # Method 6: By span with text inside link
                (By.XPATH, "//a[.//span[contains(text(), 'My Saved Searches')]]", "span inside link"),
                # Method 7: Span parent
                (By.XPATH, "//span[contains(text(), 'My Saved Searches')]/parent::a", "span parent"),
                # Method 8: Case insensitive
                (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'saved search')]", "case insensitive"),
            ]
            
            saved_searches_clicked = False
            for by, selector, description in link_selectors:
                try:
                    print(f"   Trying: {description}...")
                    
                    # Use a shorter wait for each attempt (5 seconds)
                    wait_short = WebDriverWait(self.driver, 5)
                    saved_searches_link = wait_short.until(
                        EC.presence_of_element_located((by, selector))
                    )
                    
                    # Make sure it's visible
                    if not saved_searches_link.is_displayed():
                        print(f"      Element found but not visible")
                        continue
                    
                    print(f"      Found! Text: '{saved_searches_link.text}'")
                    print(f"      href: {saved_searches_link.get_attribute('href')}")
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", saved_searches_link)
                    time.sleep(0.5)
                    
                    # Try regular click first
                    try:
                        saved_searches_link.click()
                        saved_searches_clicked = True
                        print("✅ Clicked 'My Saved Searches' (regular click)")
                        break
                    except Exception as click_err:
                        # Try JavaScript click
                        print(f"      Regular click failed, trying JS click...")
                        self.driver.execute_script("arguments[0].click();", saved_searches_link)
                        saved_searches_clicked = True
                        print("✅ Clicked 'My Saved Searches' (JS click)")
                        break
                        
                except Exception as e:
                    print(f"      Failed: {str(e)[:80]}")
                    continue
            
            if not saved_searches_clicked:
                print("\n❌ Could not find 'My Saved Searches' link after trying all methods")
                self.driver.save_screenshot("/content/my_saved_searches_not_found.png")
                
                # Save page source for debugging
                try:
                    with open("/content/dropdown_page_source.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("   Page source saved to: /content/dropdown_page_source.html")
                except:
                    pass
                
                return False
            
            time.sleep(3)
            print("✅ Saved Searches page loaded")
            return True
            
        except Exception as e:
            print(f"❌ Error navigating to Saved Searches: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def click_cama_vs_mls_search(self):
        """Step 4: Click on the CAMAvsMLS saved search"""
        print("\n" + "="*70)
        print("STEP 4: CLICK CAMAvsMLS SEARCH")
        print("="*70)
        
        try:
            time.sleep(2)
            
            search_clicked = False
            
            # Method 1: By exact ID
            try:
                search_link = self.wait.until(
                    EC.element_to_be_clickable((
                        By.ID, 
                        "m_sscv_m_lvSS_ssdi_2538498_ssv_m_aNameToggleAppearance"
                    ))
                )
                search_link.click()
                search_clicked = True
                print("✅ Clicked CAMAvsMLS (by ID)")
            except Exception as e:
                print(f"   Method 1 failed: {e}")
            
            # Method 2: By text content
            if not search_clicked:
                try:
                    search_link = self.driver.find_element(
                        By.XPATH, 
                        "//a[contains(text(), 'CAMAvsMLS')]"
                    )
                    search_link.click()
                    search_clicked = True
                    print("✅ Clicked CAMAvsMLS (by text)")
                except Exception as e:
                    print(f"   Method 2 failed: {e}")
            
            if not search_clicked:
                print("❌ Could not find CAMAvsMLS search")
                self.driver.save_screenshot("/content/saved_searches_page.png")
                return False
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Error clicking CAMAvsMLS: {e}")
            return False
    
    def click_results_button(self):
        """Step 5: Click the Results button"""
        print("\n" + "="*70)
        print("STEP 5: CLICK RESULTS BUTTON")
        print("="*70)
        
        try:
            time.sleep(2)
            
            results_clicked = False
            
            try:
                results_btn = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "m_sscv_m_lvSS_ssdi_2538498_ssv_m_lbLoadSearch"))
                )
                results_btn.click()
                results_clicked = True
                print("✅ Clicked Results button (by ID)")
            except:
                try:
                    results_btn = self.driver.find_element(
                        By.XPATH,
                        "//a[contains(text(), 'Results')]"
                    )
                    results_btn.click()
                    results_clicked = True
                    print("✅ Clicked Results button (by text)")
                except:
                    pass
            
            if not results_clicked:
                print("❌ Could not find Results button")
                self.driver.save_screenshot("/content/results_button_not_found.png")
                return False
            
            time.sleep(3)
            print("✅ Results page loaded")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking Results: {e}")
            return False
    
    def click_check_all(self):
        """Step 6: Click Check All checkbox"""
        print("\n" + "="*70)
        print("STEP 6: CHECK ALL PROPERTIES")
        print("="*70)
        
        try:
            time.sleep(2)
            
            check_all_clicked = False
            
            try:
                check_all = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "m_ucResultsPanel_m_ucSearchResults_m_cbCheckAll"))
                )
                check_all.click()
                check_all_clicked = True
                print("✅ Clicked Check All (by ID)")
            except:
                try:
                    check_all = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "input[type='checkbox'][id*='CheckAll']"
                    )
                    check_all.click()
                    check_all_clicked = True
                    print("✅ Clicked Check All (by CSS)")
                except:
                    pass
            
            if not check_all_clicked:
                print("❌ Could not find Check All checkbox")
                self.driver.save_screenshot("/content/check_all_not_found.png")
                return False
            
            time.sleep(2)
            print("✅ All properties checked")
            return True
            
        except Exception as e:
            print(f"❌ Error checking all: {e}")
            return False
    
    def click_export_button(self):
        """Step 7: Click the Export button"""
        print("\n" + "="*70)
        print("STEP 7: CLICK EXPORT BUTTON")
        print("="*70)
        
        try:
            time.sleep(2)
            
            export_clicked = False
            
            try:
                export_span = self.wait.until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "span.icon_export"
                    ))
                )
                export_span.click()
                export_clicked = True
                print("✅ Clicked Export button (by class)")
            except:
                try:
                    export_link = self.driver.find_element(
                        By.XPATH,
                        "//span[contains(@class, 'icon_export')]/parent::a"
                    )
                    export_link.click()
                    export_clicked = True
                    print("✅ Clicked Export link (by parent)")
                except:
                    pass
            
            if not export_clicked:
                print("❌ Could not find Export button")
                self.driver.save_screenshot("/content/export_button_not_found.png")
                return False
            
            time.sleep(3)
            print("✅ Export dialog opened")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking Export: {e}")
            return False
    
    def select_c3_format(self):
        """Step 8: Select C3 format from dropdown"""
        print("\n" + "="*70)
        print("STEP 8: SELECT C3 FORMAT")
        print("="*70)
        
        try:
            time.sleep(2)
            
            format_selected = False
            
            try:
                dropdown = self.wait.until(
                    EC.presence_of_element_located((By.ID, "m_ddExport"))
                )
                select = Select(dropdown)
                select.select_by_value("ud11476")  # C3 option
                format_selected = True
                print("✅ Selected C3 format (by value)")
                
            except:
                try:
                    dropdown = self.driver.find_element(By.ID, "m_ddExport")
                    select = Select(dropdown)
                    select.select_by_visible_text("C3")
                    format_selected = True
                    print("✅ Selected C3 format (by text)")
                except:
                    pass
            
            if not format_selected:
                print("❌ Could not select C3 format")
                self.driver.save_screenshot("/content/format_dropdown_error.png")
                return False
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Error selecting format: {e}")
            return False
    
    def click_final_export_button(self):
        """Step 9: Click the final Export button to download"""
        print("\n" + "="*70)
        print("STEP 9: CLICK FINAL EXPORT BUTTON")
        print("="*70)
        
        try:
            time.sleep(2)
            
            export_clicked = False
            
            try:
                final_export_btn = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "m_btnExport"))
                )
                final_export_btn.click()
                export_clicked = True
                print("✅ Clicked final Export button (by ID)")
            except:
                try:
                    final_export_btn = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "a[id='m_btnExport']"
                    )
                    final_export_btn.click()
                    export_clicked = True
                    print("✅ Clicked final Export button (by CSS)")
                except:
                    pass
            
            if not export_clicked:
                print("❌ Could not find final Export button")
                self.driver.save_screenshot("/content/final_export_button_error.png")
                return False
            
            print("✅ Export initiated!")
            print("\n⏳ Waiting for CSV download to complete...")
            time.sleep(10)
            
            print("\n" + "="*70)
            print("✅ EXPORT COMPLETE!")
            print("="*70)
            print("\n📥 Your CSV file has been downloaded to /content/")
            print("   Use the file browser on the left to find and download it.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error clicking final Export: {e}")
            return False
    
    def run_full_workflow(self, username, password):
        """Run the complete workflow"""
        print("\n" + "="*70)
        print("MLS MATRIX - NATIVE EXPORT WORKFLOW (COLAB)")
        print("="*70)
        print("\nThis will:")
        print("1. Login")
        print("2. Click Matrix icon (enters Matrix application)")
        print("3. Navigate to Saved Searches (hover My Matrix menu)")
        print("4. Click CAMAvsMLS search")
        print("5. Click Results")
        print("6. Check All properties")
        print("7. Click Export button")
        print("8. Select C3 format")
        print("9. Click final Export button")
        print("10. Download CSV file")
        print("="*70)
        
        # Execute each step
        if not self.login(username, password):
            return False
        
        if not self.click_matrix_icon():
            print("\n❌ Failed to click Matrix icon - cannot continue")
            return False
        
        if not self.navigate_to_saved_searches():
            return False
        
        if not self.click_cama_vs_mls_search():
            return False
        
        if not self.click_results_button():
            return False
        
        if not self.click_check_all():
            return False
        
        if not self.click_export_button():
            return False
        
        if not self.select_c3_format():
            return False
        
        if not self.click_final_export_button():
            return False
        
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE!")
        print("="*70)
        print("\n📊 Your data has been exported using MLS Matrix's native export.")
        print("   Check /content/ folder for your CSV file!")
        
        return True
    
    def close(self):
        """Close the browser"""
        print("\n🔒 Closing browser...")
        self.driver.quit()
        print("✅ Browser closed")


# ============================================================================
# RUN THE WORKFLOW
# ============================================================================

def main():
    print("\n" + "="*70)
    print("MLS MATRIX - CAMA vs MLS NATIVE EXPORT (COLAB)")
    print("="*70)
    print("\nThis uses MLS Matrix's built-in export feature for clean CSV output!")
    
    # Get credentials
    from getpass import getpass
    username = input("\nMLS Username: ")
    password = getpass("MLS Password: ")
    
    # Create exporter
    exporter = CustomMLSExporter()
    
    try:
        # Run the full workflow
        success = exporter.run_full_workflow(username, password)
        
        if success:
            print("\n✅ Success! Check /content/ folder for the CSV file.")
            print("   You can download it from the file browser on the left.")
        else:
            print("\n⚠️ Workflow completed with some issues")
            print("   Check /content/ for screenshots for debugging")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        exporter.close()


if __name__ == "__main__":
    main()
