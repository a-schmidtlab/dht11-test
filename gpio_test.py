import lgpio
import time

def main():
    print("Starting GPIO test...")
    try:
        # Open the GPIO chip
        h = lgpio.gpiochip_open(0)
        
        # Configure GPIO17 as output
        lgpio.gpio_claim_output(h, 17)
        
        # Blink the LED 5 times
        for i in range(5):
            print(f"Setting GPIO17 HIGH (iteration {i+1})")
            lgpio.gpio_write(h, 17, 1)
            time.sleep(1)
            print(f"Setting GPIO17 LOW (iteration {i+1})")
            lgpio.gpio_write(h, 17, 0)
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Cleanup done")
        try:
            # Release the GPIO
            lgpio.gpio_free(h, 17)
            lgpio.gpiochip_close(h)
        except:
            pass

if __name__ == "__main__":
    main() 