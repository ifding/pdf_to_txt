import argparse
from util import check_folder
from trainers.simclr import SimCLRTrainer


"""parsing and configuration"""
def parse_args():
    desc = "Tensorflow implementation of SimCLR"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--phase', type=str, default='train', help='train or test ?')
    parser.add_argument('--dataset', type=str, default='cifar10', help='cifar10, cifar100, tiny')

    parser.add_argument('--model', type=str, default='simclr', help='simclr, deepcluster')
    parser.add_argument('--epoch', type=int, default=10, help='The number of epochs to run')
    parser.add_argument('--batch_size', type=int, default=256, help='The size of batch per gpu')
    parser.add_argument('--res_n', type=int, default=50, help='18, 34, 50, 101, 152')

    parser.add_argument('--lr', type=float, default=0.3, help='learning rate')

    parser.add_argument('--log_dir', type=str, default='logs',
                        help='Directory name to save training logs')

    return check_args(parser.parse_args())

"""checking arguments"""
def check_args(args):

    # --result_dir
    check_folder(args.log_dir)

    # --epoch
    try:
        assert args.epoch >= 1
    except:
        print('number of epochs must be larger than or equal to one')

    # --batch_size
    try:
        assert args.batch_size >= 1
    except:
        print('batch size must be larger than or equal to one')
    return args

"""main"""
def main():
    # parse arguments
    args = parse_args()
    if args is None:
        exit()

    fcn = None
    if args.res_n == 50:
        fcn = 'ResNet50'

    if args.model == 'simclr':
        trainer = SimCLRTrainer(logdir=args.log_dir, trainingdata=args.dataset, \
                fcn=fcn, lr=args.lr)
    trainer.fit(args.epoch)
    print(" [*] Training finished! \n")    
    
    trainer.evaluate()
    print(" [*] Evaluation finished!")

if __name__ == '__main__':
    main()
