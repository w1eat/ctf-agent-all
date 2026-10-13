#import <IOBluetooth/IOBluetooth.h>

int main(void)
{
  NSArray *devices = [IOBluetoothDevice pairedDevices];
  int count = [devices count];
  for ( int i = 0; i < count; i++ )
  {
    IOBluetoothDevice *device = [devices objectAtIndex:i];
    NSLog(@"%@:\n", [device name]);
    NSLog(@"  paired:    %d\n", [device isPaired]);
    NSLog(@"  connected: %d\n", [device isConnected]);
  }
  return 0;
}
