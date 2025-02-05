import lgpio
import time

def cleanup():
    print("Cleaning up GPIO...")
    try:
        for i in range(4):
            try:
                h = lgpio.gpiochip_open(i)
                for pin in [4, 17, 23]:  # Added GPIO23
                    try:
                        lgpio.gpio_free(h, pin)
                    except:
                        pass
                lgpio.gpiochip_close(h)
            except:
                pass
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    cleanup()
    print("Cleanup complete") 