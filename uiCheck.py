from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import time



class Credentials:
    username = "guest@oceanpowertech.com"
    password = ""


def radarManip( driver, ac ):
    print("Not implemented yet")


def videoManip( driver, ac, numPans = 5):
    sl = 1.0
    button = driver.find_element(By.XPATH,'//button[@title="Maximize"]')
    button.click()
    time.sleep( sl ) 
    button = driver.find_element(By.XPATH,'//button[@title="Toggle Thermal"]')
    button.click()
    time.sleep( sl )
    
    


def mapManip(driver, ac, numZooms = 5, mapsettle = 15):
    print(f"Allowing {mapsettle}s for map to localize...")
    time.sleep( mapsettle )
    print("Testing map functionality")
    geoMap = driver.find_element(By.ID,"map")
    scale = driver.find_element(By.CLASS_NAME,"leaflet-control-scale-line")
    sl = 1 
    print(f"1NM screen scale: {scale.size['width']}")
    ##### Zoom #################
    for elem,sl,command in zip ((driver.find_element(By.CLASS_NAME, 'leaflet-control-zoom-out'),
                                 driver.find_element(By.CLASS_NAME, 'leaflet-control-zoom-in')),
                                (2,2),
                                ("out","in")):
        i = 0
        print(f"Zoooming {command} {numZooms} times...")
        while i < numZooms:
            elem.click()
            time.sleep( sl )
            i+=1
    sl = 1.0  # Reduce sleep time for next tests
    ##### Polyline ##############
    print("Measuring distance")
    elem = driver.find_element(By.CLASS_NAME, 'leaflet-draw-draw-polyline')
    elem.click()
    time.sleep( sl )
    ac.move_to_element(geoMap).move_by_offset(60, 80).click().perform()
    ac.move_to_element(geoMap).move_by_offset(0, 0).click().perform()
    time.sleep( sl )
    ##### Draw ZOI ##########
    print("Creating zone of interest")
    elem = driver.find_element(By.CLASS_NAME, 'leaflet-draw-draw-polygon')
    elem.click()
    time.sleep( sl )
    for lat,lon in zip([0,75],[-100,-250]):
        #print(f"Plotting coordinate at {lat}-{lon}")
        time.sleep( sl )
        ac.move_to_element(geoMap).move_by_offset(lat, lon).click().perform()
    #----- ZOI Popup Window -----#
    elem = driver.find_element_by_xpath("//div[@title='#007F54']")
    elem.click()
    time.sleep( sl )
    elem = driver.find_element(By.NAME,'zoneName')
    elem.send_keys("SeleniumTZ")
    time.sleep( sl )
    elem = driver.find_element(By.CLASS_NAME,'zoi-button')
    elem.click()                           
    ##### Slew to pos ###########
    print("Slewing camera from map")
    time.sleep(sl)
    elem = driver.find_element(By.CLASS_NAME, 'leaflet-control-button.slew-btn')
    elem.click()
    for lat,lon in zip([0,100,0,-100],[100,0,-100,0]):
        time.sleep( sl*3 )
        ac.move_to_element(geoMap).move_by_offset(lat, lon).click().perform()
    elem = driver.find_element(By.CLASS_NAME, "leaflet-slew-cancel.leaflet-slew-cancel-active")
    elem.click()
    time.sleep( sl )
    #### Delete layers ########
    print("Deleting layers")
    elem = driver.find_element(By.CLASS_NAME, "leaflet-draw-edit-remove")
    elem.click()
    time.sleep( sl )
    elem = driver.find_element(By.XPATH, "//a[@title='Clear all layers']")
    elem.click()
    print("Map functionality test complete.")
    return driver


def functionalChecks( driver ):
    driver.get("https://staging-opt.fconnect.fathom5.io/dashboard")
    ac = ActionChains(driver)
    for func in (mapManip, videoManip, radarManip):
        driver = func( driver, ac )
        time.sleep( 2 )
    return driver
    
    
    
def F5_login( driver ):
    print("Beginning screen record")
    driver.get("https://staging-opt.fconnect.fathom5.io/login")
    title = driver.title
    assert title == "Maritime Domain Awareness Solution"
    driver.implicitly_wait(0.5)
    user_box = driver.find_element(by=By.NAME, value="username")
    pswd_box = driver.find_element(by=By.NAME, value="password")
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
    user_box.send_keys( Credentials.username )
    pswd_box.send_keys( Credentials.password )
    submit_button.click()
    time.sleep(1.5)
    return driver
    

def main( args ):
    driver = webdriver.Chrome('/usr/local/chromedriver')                       
    driver = F5_login( driver )
    driver = functionalChecks( driver )
    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-pw', '--password', default = None, help="Add password for F5 login")
    parser.add_argument("-i","--inPath", default = None,
                        help="inputPath to file, no entry defaults to first path matching $PWD/*.mpeg")
    parser.add_argument("-o","--outPath", default = None,
                        help="outputPath to write logging file, if enabled with -v, defaults to $PWD/output.log")
    parser.add_argument("-v","--verbose", action = "store_true", default = False, help="Enable additional logging")
    args = parser.parse_args()
    main( args )



